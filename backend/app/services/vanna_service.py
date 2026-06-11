"""app/services/vanna_service.py
One Vanna instance per DB instance, lazily created and cached.
Uses OpenAI as the LLM backend.
"""
import os
import re
import threading
from typing import Optional

from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore

from app.core.config import get_settings
from app.db.connection_manager import get_connection, INSTANCE_CONN_STRINGS

settings = get_settings()

_INTROSPECTION_MARKER = "allow_llm_to_see_data"

# ─── Schema cache: instance_key → {table: [col, ...]} ────────────────────────
_schema_cache: dict[str, dict[str, list[str]]] = {}
_schema_lock = threading.Lock()


# ─── Custom Vanna class combining OpenAI + ChromaDB ──────────────────────────

class OpenAIVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config: dict):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

    def get_sql_prompt(self, question: str, question_sql_list, ddl_list, doc_list, **kwargs):
        """
        Override Vanna's default prompt builder to inject a strict
        schema-awareness constraint at the top of the system message.
        """
        prompt = super().get_sql_prompt(
            question=question,
            question_sql_list=question_sql_list,
            ddl_list=ddl_list,
            doc_list=doc_list,
            **kwargs,
        )

        schema_block = kwargs.get("schema_constraint", "")
        if schema_block:
            constraint = (
                "STRICT RULES — you MUST follow these before writing any SQL:\n"

                "1. Only use tables and columns listed in the schema below. "
                "Do NOT invent, guess, or abbreviate any table or column name.\n"

                "2. Understand semantic equivalents, business terminology, and synonyms. "
                "Map user concepts to the most appropriate table and column available in "
                "the schema. Examples: employee/staff/personnel, committee/board/panel, "
                "member/user/person, department/division/unit, etc. "
                "Use schema columns that represent the requested concept even if the user "
                "uses different wording.\n"

                "3. NEVER change user-provided values. Any names, titles, codes, numbers, "
                "dates, identifiers, remarks, committee names, member names, or other "
                "filter values mentioned by the user must be preserved exactly as provided. "
                "Do not correct spelling, expand abbreviations, translate, normalize, "
                "rephrase, or substitute them.\n"

                "4. Use NO_MATCH ONLY when the user asks for a concept whose data is stored "
                "in NO column in the schema. "
                "Do NOT return NO_MATCH because a user-supplied value is not visible in the "
                "schema. Values are runtime data and are never expected to appear in the schema.\n"

                "5. Never use SELECT *. Always name columns explicitly.\n"

                "6. For entity names, titles, descriptions, remarks, addresses, dates, time "
                "and other free-text/searchable columns, use LIKE with wildcards.\n"
                "Examples:\n"
                "   MemberName LIKE '%John%'\n"
                "   CommitteeName LIKE '%Finance%'\n"
                "   Remarks LIKE '%meeting%'\n"
                "   Time LIKE '%6:30 PM%'\n\n"

                "7. For categorical or enumerated columns (Gender, Status, Type, ActiveFlag, "
                "MaritalStatus, approval states, Yes/No flags, codes, etc.), use exact "
                "matching (=) unless the user explicitly requests a partial search.\n"
                "Examples:\n"
                "   Gender = 'Male'\n"
                "   Status = 'Active'\n"
                "   ActiveFlag = 'Y'\n\n"

                "8. To find attachments for an agenda, filter MtAttachment_Source = 'MeetingAgenda'"
                "To find attachments for MoM, filter MtAttachment_Source = 'MoM'"
                "To find attachments for MoM Miscellaneous, filter MtAttachment_Source = 'MoM_Miscellaneous'"

                "IMPORTANT: Do NOT use LIKE for categorical values where one value may be a "
                "substring of another.\n\n"

                f"AVAILABLE SCHEMA:\n{schema_block}\n"
                "─────────────────────────────────────────\n"
            )
            # Prepend to the first system message
            if isinstance(prompt, list):
                for msg in prompt:
                    if isinstance(msg, dict) and msg.get("role") == "system":
                        msg["content"] = constraint + msg["content"]
                        break
                else:
                    prompt.insert(0, {"role": "system", "content": constraint})

        return prompt


# ─── Registry of per-instance Vanna objects ──────────────────────────────────

_instances: dict[str, OpenAIVanna] = {}
_lock = threading.Lock()


def _make_vanna(instance_key: str) -> OpenAIVanna:
    persist_path = os.path.join(settings.chroma_persist_dir, instance_key)
    os.makedirs(persist_path, exist_ok=True)

    vn = OpenAIVanna(config={
        "api_key": settings.openai_api_key,
        "model": "gpt-5.1",
        "path": persist_path,
        "collection_name": f"vanna_{instance_key}",
        "allow_llm_to_see_data": True,
    })

    conn_str = INSTANCE_CONN_STRINGS[instance_key]
    vn.connect_to_mssql(odbc_conn_str=conn_str)
    return vn


def get_vanna(instance_key: str) -> OpenAIVanna:
    """Return (and cache) the Vanna instance for this DB instance."""
    if instance_key not in _instances:
        with _lock:
            if instance_key not in _instances:
                _instances[instance_key] = _make_vanna(instance_key)
    return _instances[instance_key]


# ─── Schema loading & formatting ─────────────────────────────────────────────

def _load_schema(instance_key: str) -> dict[str, list[str]]:
    """
    Query INFORMATION_SCHEMA to get all user tables and their columns.
    Result is cached for the lifetime of the process.
    """
    if instance_key in _schema_cache:
        return _schema_cache[instance_key]

    with _schema_lock:
        if instance_key in _schema_cache:
            return _schema_cache[instance_key]

        vn = get_vanna(instance_key)
        df = vn.run_sql("""
            SELECT
                t.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE
            FROM INFORMATION_SCHEMA.TABLES  t
            JOIN INFORMATION_SCHEMA.COLUMNS c
              ON  c.TABLE_NAME   = t.TABLE_NAME
              AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
            WHERE t.TABLE_TYPE   = 'BASE TABLE'
              AND t.TABLE_SCHEMA = 'dbo'
            ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
        """)

        schema: dict[str, list[str]] = {}
        if df is not None:
            for _, row in df.iterrows():
                tbl = row["TABLE_NAME"]
                col = f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})"
                schema.setdefault(tbl, []).append(col)

        _schema_cache[instance_key] = schema
        return schema


def _format_schema_block(schema: dict[str, list[str]]) -> str:
    """
    Render the schema as a compact, readable block for the prompt.
    Example:
        Users: id (int), name (nvarchar), email (nvarchar)
        Orders: id (int), user_id (int), total (decimal)
    """
    lines = []
    for table, cols in schema.items():
        lines.append(f"  {table}: {', '.join(cols)}")
    return "\n".join(lines)


def invalidate_schema_cache(instance_key: Optional[str] = None) -> None:
    """Call this after DDL changes so the schema is re-fetched on next query."""
    with _schema_lock:
        if instance_key:
            _schema_cache.pop(instance_key, None)
        else:
            _schema_cache.clear()


# ─── SQL column/table validator ───────────────────────────────────────────────

def _validate_sql_against_schema(sql: str, schema: dict[str, list[str]]) -> Optional[str]:
    if not schema:
        return None

    sql_upper = sql.upper()
    known_tables_upper = {t.upper() for t in schema}

    # ── Table check ───────────────────────────────────────────────────────────
    table_tokens = re.findall(
        r'(?:FROM|JOIN)\s+(?:\[?dbo\]?\.)?\[?(\w+)\]?',
        sql_upper,
    )
    unknown_tables = [t for t in table_tokens if t not in known_tables_upper]
    if unknown_tables:
        readable = ", ".join(unknown_tables)
        return (
            f"The query references table(s) that don't exist in the database: {readable}. "
            "Please rephrase your question using the data that is actually available."
        )

    # ── Build alias set ───────────────────────────────────────────────────────
    # Table aliases:  "FROM RuUsers u"  or  "JOIN RuUsers AS u"
    table_alias_pattern = re.findall(
        r'(?:FROM|JOIN)\s+(?:\[?dbo\]?\.)?\[?\w+\]?\s+(?:AS\s+)?(\w+)',
        sql_upper,
    )
    # Column/expression aliases:  "COUNT(*) AS TotalMeetings",  "x AS MyCol"
    col_alias_pattern = re.findall(r'\bAS\s+(\w+)', sql_upper)

    known_aliases_upper = set(table_alias_pattern) | set(col_alias_pattern)

    # ── Strip string literals AND comments so their words aren't tokenized ────
    sql_no_strings = re.sub(r"'[^']*'", "", sql)
    sql_no_strings = re.sub(r"--[^\n]*", "", sql_no_strings)
    sql_no_strings = re.sub(r"/\*.*?\*/", "", sql_no_strings, flags=re.DOTALL)

    # ── Column check ─────────────────────────────────────────────────────────
    all_known_cols_upper = {
        col.split(" ")[0].upper()
        for cols in schema.values()
        for col in cols
    }

    sql_keywords = {
        # DML / clauses
        "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
        "ON", "AND", "OR", "NOT", "IN", "IS", "NULL", "AS", "GROUP", "BY",
        "ORDER", "HAVING", "DISTINCT", "TOP", "COUNT", "SUM", "AVG", "MIN",
        "MAX", "CASE", "WHEN", "THEN", "ELSE", "END", "WITH", "SET",
        "INSERT", "UPDATE", "DELETE", "EXEC", "EXECUTE",
        "CROSS", "FULL", "PARTITION", "OVER", "UNION", "ALL", "INTO", "VALUES",
        "ASC", "DESC", "LIMIT", "OFFSET", "LIKE", "BETWEEN", "EXISTS",
        # Data types
        "INT", "BIGINT", "SMALLINT", "TINYINT", "BIT",
        "DECIMAL", "NUMERIC", "FLOAT", "REAL", "MONEY", "SMALLMONEY",
        "CHAR", "VARCHAR", "NCHAR", "NVARCHAR", "TEXT", "NTEXT",
        "DATE", "TIME", "DATETIME", "DATETIME2", "SMALLDATETIME", "DATETIMEOFFSET",
        "BINARY", "VARBINARY", "IMAGE", "UNIQUEIDENTIFIER", "XML", "SQL_VARIANT",
        # Conversion / scalar functions
        "CAST", "CONVERT", "TRY_CONVERT", "TRY_CAST", "PARSE", "TRY_PARSE",
        "COALESCE", "ISNULL", "NULLIF", "IIF", "CHOOSE",
        "LEN", "LEFT", "RIGHT", "SUBSTRING", "CHARINDEX", "PATINDEX",
        "UPPER", "LOWER", "LTRIM", "RTRIM", "TRIM", "REPLACE", "STUFF", "CONCAT",
        "GETDATE", "GETUTCDATE", "SYSDATETIME", "SYSUTCDATETIME",
        "DATEPART", "DATEDIFF", "DATEADD", "DATEFROMPARTS", "EOMONTH",
        "YEAR", "MONTH", "DAY", "ISDATE", "FORMAT",
        "ROW_NUMBER", "RANK", "DENSE_RANK", "NTILE", "LAG", "LEAD",
        "FIRST_VALUE", "LAST_VALUE",
        "ABS", "CEILING", "FLOOR", "ROUND", "POWER", "SQRT", "SIGN",
        "NEWID", "SCOPE_IDENTITY",
        # Schema qualifiers
        "DBO", "SYS", "INFORMATION_SCHEMA", "ROWS", "FETCH", "NEXT", "ONLY",
    }

    col_tokens = re.findall(r'\b([A-Za-z_]\w*)\b', sql_no_strings)

    unknown_cols = [
        tok for tok in col_tokens
        if tok.upper() not in sql_keywords
        and tok.upper() not in known_tables_upper
        and tok.upper() not in known_aliases_upper      # table aliases + AS aliases
        and tok.upper() not in all_known_cols_upper
        and not tok.isdigit()
        and len(tok) > 1
    ]

    if unknown_cols:
        readable = ", ".join(dict.fromkeys(unknown_cols))
        return (
            f"The query uses column(s) that don't exist in the database: {readable}. "
            "Please check your question — those fields may be named differently or not tracked at all."
        )

    return None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_valid_sql(text: str) -> bool:
    if not text:
        return False
    stripped = text.strip().lstrip("(").upper()
    return bool(re.match(
        r"^(SELECT|INSERT|UPDATE|DELETE|WITH|EXEC|EXECUTE|CREATE|DROP|ALTER|MERGE)",
        stripped,
    ))


# ─── Public query runner ──────────────────────────────────────────────────────

def run_query(instance_key: str, question: str) -> dict:
    """
    Generate SQL → Validate → Execute.

    Returns { sql, results, error }.
    """
    vn = get_vanna(instance_key)

    # Load and format the real schema for this instance
    schema = _load_schema(instance_key)
    schema_block = _format_schema_block(schema)

    try:
        sql = vn.generate_sql(
            question=question,
            allow_llm_to_see_data=True,
            schema_constraint=schema_block,
        )

        # ── Guard: nothing returned ───────────────────────────────────────────
        if not sql:
            return {
                "sql": None, "results": None,
                "error": "Could not generate SQL for that question.",
            }

        # ── Guard: LLM signalled no match (our NO_MATCH protocol) ────────────
        if sql.strip().startswith("NO_MATCH:"):
            user_msg = sql.strip().removeprefix("NO_MATCH:").strip()
            return {
                "sql": None, "results": None,
                "error": user_msg,
            }

        # ── Guard: Vanna introspection blocker ────────────────────────────────
        if _INTROSPECTION_MARKER in sql:
            return {
                "sql": None, "results": None,
                "error": (
                    "This question requires looking at actual data values to build the query. "
                    "Data introspection is now enabled — please try again."
                ),
            }

        # ── Guard: output doesn't look like SQL ───────────────────────────────
        if not _is_valid_sql(sql):
            return {
                "sql": None, "results": None,
                "error": f"The model returned an unexpected response instead of SQL: {sql[:200]}",
            }

        # ── Guard: lexical schema validation ──────────────────────────────────
        schema_error = _validate_sql_against_schema(sql, schema)
        if schema_error:
            return {
                "sql": None, "results": None,
                "error": schema_error,
            }

        # ── Execute ───────────────────────────────────────────────────────────
        df = vn.run_sql(sql)
        if df is not None:
            import pandas as pd

            def sanitize(val):
                if val is None:
                    return None
                try:
                    if pd.isna(val):
                        return None
                except (TypeError, ValueError):
                    pass
                if isinstance(val, float) and val.is_integer():
                    return int(val)
                return val

            results = [
                {k: sanitize(v) for k, v in record.items()}
                for record in df.to_dict(orient="records")
            ]
        else:
            results = []

        return {
            "sql": sql,
            "results": results,
            "error": None,
        }

    except Exception as e:
        err = str(e)
        if _INTROSPECTION_MARKER in err:
            return {
                "sql": None, "results": None,
                "error": "Data introspection was required. allow_llm_to_see_data is enabled — please retry.",
            }
        return {
            "sql": None, "results": None,
            "error": err,
        }


# ─── Training helpers ─────────────────────────────────────────────────────────

def debug_vanna(instance_key: str, question: str):
    vn = get_vanna(instance_key)
    df = vn.get_training_data()
    print("Total training records:", len(df) if df is not None else 0)
    if df is not None:
        print(df[['training_data_type', 'question', 'content']].to_string())
    print("\nSimilar Q&A:", vn.get_similar_question_sql(question))
    print("\nRelated DDL:", vn.get_related_ddl(question))
    print("\nRelated docs:", vn.get_related_documentation(question))


def train_ddl(instance_key: str, ddl: str) -> None:
    invalidate_schema_cache(instance_key)   # schema may have changed
    get_vanna(instance_key).train(ddl=ddl)


def train_documentation(instance_key: str, doc: str) -> None:
    get_vanna(instance_key).train(documentation=doc)


def train_qa(instance_key: str, question: str, sql: str) -> None:
    get_vanna(instance_key).train(question=question, sql=sql)


def remove_training_data(instance_key: str, training_id: str) -> bool:
    return get_vanna(instance_key).remove_training_data(id=training_id)


def get_training_data(instance_key: str) -> list[dict]:
    df = get_vanna(instance_key).get_training_data()
    return [] if df is None else df.to_dict(orient="records")