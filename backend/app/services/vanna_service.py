"""app/services/vanna_service.py
One Vanna instance per DB instance, lazily created and cached.
Uses OpenAI as the LLM backend.

Intent normalization is applied to every incoming question before SQL generation
so that synonym variations ("participants", "attendees", "sessions", etc.) are
transparently resolved to the canonical vocabulary used in training data and
documentation.

RMS routing:
  The "it_rms" instance uses a completely separate system prompt (built by
  _build_rms_constraint) and a separate NL-summary domain-knowledge block,
  because its schema/vocabulary has nothing to do with MeetingSphere. All
  other plumbing (caching, get_vanna, train_ddl, schema_fetcher calls, etc.)
  stays unified so existing admin/training routes don't need to change.
"""
import os
import re
import threading
from typing import Optional

from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore

from app.core.config import get_settings
from app.db.connection_manager import get_connection, INSTANCE_CONN_STRINGS
from app.services.intent_normalizer import normalize_question

settings = get_settings()

_INTROSPECTION_MARKER = "allow_llm_to_see_data"
_RMS_INSTANCE_KEY = "it_rms"

# ─── Schema cache: instance_key → {table: [col, ...]} ────────────────────────
_schema_cache: dict[str, dict[str, list[str]]] = {}
_schema_lock = threading.Lock()


# ─── Per-instance system prompt builders ─────────────────────────────────────

def _build_meetingsphere_constraint(now_str: str, schema_block: str) -> str:
    return (
        f"CURRENT DATETIME: {now_str}\n\n"
        "STRICT RULES — you MUST follow these before writing any SQL:\n"
        "1. Only use tables and columns listed in the schema below. "
        "Do NOT invent, guess, or abbreviate any table or column name.\n"

        "2. Use NO_MATCH ONLY when the user asks for a concept whose data is stored "
        "in NO column in the schema (e.g. 'salary' when no salary column exists). "
        "NEVER return NO_MATCH just because a specific name, value, or keyword "
        "mentioned by the user (e.g. '13AP Com', 'Finance Board', 'John') does not "
        "appear in the schema — those are filter VALUES, not column names. "
        "Filter values are supplied by the user at runtime and are never listed in "
        "the schema. When the user mentions a name or value, use the appropriate "
        "filtering strategy based on the column type.\n"

        "3. Never use SELECT *. Always name columns explicitly.\n\n"

        "4. Whenever searching for values in any case, use the SQL LIKE operator with wildcards.\n"
        "Examples:\n"
        "   MemberName LIKE '%John%'\n"
        "   CommitteeName LIKE '%Finance%'\n"
        "   Remarks LIKE '%meeting%'\n"
        "   Time LIKE '%6:30 PM%'\n\n"
        "   MeetingTitle LIKE '%11 June meeting with agenda items%'\n\n"

        "5. For categorical or enumerated columns (e.g. Gender, Status, Type, "
        "ActiveFlag, MaritalStatus, Yes/No fields, approval states, codes, or "
        "other fixed-value fields), use exact matching (=) instead of LIKE unless "
        "the user explicitly requests a partial search.\n"
        "Examples:\n"
        "   Gender = 'Male'\n"
        "   Status = 'Active'\n"
        "   ActiveFlag = 'Y'\n\n"

        "IMPORTANT: Do NOT use LIKE for categorical values where one value may be "
        "a substring of another. For example, use Gender = 'Male' instead of "
        "Gender LIKE '%Male%' because it could also match 'Female'.\n\n"

        "6. If the user asks for attachments, attached files, documents, file content, "
        "downloadable files, ECM files, or any attachment-related information, you MUST "
        "include BOTH of the following columns in the SELECT list in addition to any "
        "other requested columns:\n"
        "   MtAttachment_FileName\n"
        "   MtAttachment_EcmFileId\n"
        "Never omit these columns for attachment-related queries.\n\n"

        "6b. NEVER include MtAttachment_FileContent in the SELECT list under any circumstances. "
        "This column is excluded from all query results regardless of what the user asks. "
        "Only include MtAttachment_FileName and MtAttachment_EcmFileId for attachment-related queries.\n\n"

        "6c. MtAttachment_Source is a categorical column with EXACTLY these 4 allowed values:\n"
        "   MeetingAgenda\n"
        "   MoM\n"
        "   MoM_Miscellaneous\n"
        "   SharedDocument\n"
        "When the user references an attachment source/type (e.g. 'agenda files', 'minutes', "
        "'shared documents'), filter using exact matching (=) against this column, mapped to "
        "the closest of the 4 values above. Never invent a source value outside this list, "
        "and never use LIKE for this column since values may overlap as substrings.\n\n"

        "7. RESPONSE STYLE: Be direct and minimal. "
        "MUST notify the user in these two specific cases:\n"
        "   a) No rows returned: say exactly 'No matching records found.'\n"
        "   b) The requested data exists but the value is NULL or empty "
        "(e.g. file content not extracted, field not populated): say exactly "
        "'This information has not been populated yet.'\n\n"
        "In all other cases, present results silently with no surrounding text.\n\n"

        "8. CONTEXT HISTORY: Previous questions are provided for conversational "
        "reference only (e.g. resolving 'it', 'that meeting', 'same person'). "
        "NEVER reuse, copy, or adapt SQL from previous turns. "
        "Always generate fresh SQL based solely on the current question and schema. "
        "Do NOT inherit filter values, JOIN patterns, or WHERE conditions from prior SQL.\n\n"

        "9. FILE EXTRACTION: If the user asks to extract text, read, view, open, "
        "or get content from a file — regardless of phrasing — do NOT generate any SQL. "
        "Instead, respond with exactly this and nothing else:\n"
        "NO_MATCH: To view this file, please wait for the upcoming version with download feature :)\n\n"

        f"AVAILABLE SCHEMA:\n{schema_block}\n"
        "─────────────────────────────────────────\n"
    )


def _build_rms_constraint(now_str: str, schema_block: str) -> str:
    """
    Separate, RMS-specific system prompt. No MeetingSphere attachment/status
    rules apply here — RMS has its own schema and vocabulary.
    """
    return (
        f"CURRENT DATETIME: {now_str}\n\n"
        "You are a SQL expert for the RMS (Record Management System) database.\n\n"

        "STRICT RULES — you MUST follow these before writing any SQL:\n"
        "1. Only use tables and columns listed in the schema below. "
        "Do NOT invent, guess, or abbreviate any table or column name.\n"

        "2. Use NO_MATCH ONLY when the user asks for a concept whose data is stored "
        "in NO column in the schema. NEVER return NO_MATCH just because a specific "
        "name, value, or keyword mentioned by the user does not appear in the schema "
        "— those are filter VALUES, not column names, and are supplied at runtime.\n"

        "3. Never use SELECT *. Always name columns explicitly.\n\n"

        "4. Whenever searching for free-text values (names, titles, remarks, descriptions), "
        "use the SQL LIKE operator with wildcards, e.g. RecordTitle LIKE '%contract%'.\n\n"

        "5. For categorical or enumerated columns (Status, Type, ActiveFlag, Yes/No fields, "
        "approval states, codes), use exact matching (=) instead of LIKE unless the user "
        "explicitly requests a partial search.\n\n"

        "IMPORTANT: Do NOT use LIKE for categorical values where one value may be a "
        "substring of another.\n\n"

        "6. RESPONSE STYLE: Be direct and minimal. "
        "MUST notify the user in these two specific cases:\n"
        "   a) No rows returned: say exactly 'No matching records found.'\n"
        "   b) The requested data exists but the value is NULL or empty: say exactly "
        "'This information has not been populated yet.'\n\n"
        "In all other cases, present results silently with no surrounding text.\n\n"

        "7. CONTEXT HISTORY: Previous questions are provided for conversational "
        "reference only (e.g. resolving 'it', 'that record', 'same person'). "
        "NEVER reuse, copy, or adapt SQL from previous turns. "
        "Always generate fresh SQL based solely on the current question and schema.\n\n"

        f"AVAILABLE SCHEMA:\n{schema_block}\n"
        "─────────────────────────────────────────\n"
    )


def _build_constraint(instance_key: str, now_str: str, schema_block: str) -> str:
    if instance_key == _RMS_INSTANCE_KEY:
        return _build_rms_constraint(now_str, schema_block)
    return _build_meetingsphere_constraint(now_str, schema_block)


# ─── Custom Vanna class combining OpenAI + ChromaDB ──────────────────────────

class OpenAIVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config: dict, instance_key: str):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
        self.instance_key = instance_key   # ← used to pick the right prompt

    def get_sql_prompt(self, question: str, question_sql_list, ddl_list, doc_list, **kwargs):
        """
        Override Vanna's default prompt builder to inject a strict
        schema-awareness constraint at the top of the system message.
        The constraint content is selected based on self.instance_key.
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
            from datetime import datetime as _dt
            _now = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
            constraint = _build_constraint(self.instance_key, _now, schema_block)

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

    vn = OpenAIVanna(
        config={
            "api_key": settings.openai_api_key,
            "model": "gpt-5.1",
            "path": persist_path,
            "collection_name": f"vanna_{instance_key}",   # already isolated per instance_key
            "allow_llm_to_see_data": True,
        },
        instance_key=instance_key,
    )

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
    Result is cached for the lifetime of the process, per instance_key —
    so "it_rms" gets its own cache entry, fetched from the RMS connection.
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
        return (
            "Sorry, I wasn't able to find the right data for your question. "
            "Could you try rephrasing it?"
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

    # ── Strip string literals so their words aren't tokenized ─────────────────
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
        return (
            "I couldn't find that information in the system. "
            "The data you're looking for may be stored under a different name or may not be tracked yet."
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


def _friendly_db_error(raw_error: str) -> str:
    """
    Map low-level database / API exception messages to short, human-friendly
    strings.  Falls back to a generic message so technical details never reach
    the user.
    """
    err = raw_error.lower()

    # Token / context-window limits
    if any(k in err for k in ("token", "context_length", "context length",
                               "maximum context", "max_tokens", "rate limit",
                               "rate_limit", "too many requests", "429")):
        return (
            "Your question is a bit too complex for me to process right now. "
            "Try breaking it into smaller questions or simplifying the request."
        )

    # Network / connectivity
    if any(k in err for k in ("connection", "timeout", "timed out",
                               "network", "unreachable", "refused", "reset by peer")):
        return (
            "I'm having trouble connecting to the database at the moment. "
            "Please try again in a few seconds."
        )

    # Authentication / permission
    if any(k in err for k in ("login failed", "permission", "access denied",
                               "unauthorized", "403", "401", "privilege")):
        return (
            "It looks like there's a permissions issue preventing me from "
            "fetching that data. Please contact your administrator."
        )

    # SQL syntax errors (shouldn't normally reach the user, but just in case)
    if any(k in err for k in ("syntax error", "incorrect syntax", "invalid object name",
                               "invalid column name", "ambiguous column")):
        return (
            "I had trouble building the right query for your question. "
            "Could you try rephrasing it?"
        )

    # No results / empty
    if any(k in err for k in ("no rows", "no results", "no matching")):
        return "No matching records found."

    # Generic fallback — never expose raw error text
    return (
        "Something went wrong while processing your request. "
        "Please try again, or rephrase your question."
    )


# ─── Per-instance NL-summary domain knowledge ────────────────────────────────

def _meetingsphere_domain_block() -> str:
    return (
        "DOMAIN KNOWLEDGE:\n"
        "Meeting status is stored as an integer in the database. "
        "Always translate these LuMeetingSphereLookups_StatusCode values into human-readable labels in your response:\n"
        "   0 = Cancelled\n"
        "   1 = Pending\n"
        "   2 = Ended\n"
        "   3 = Completed\n"
        "   4 = Draft\n"
        "Never show raw status numbers to the user — always use the label.\n\n"
        "ATTACHMENT LINKS:\n"
        "If the results contain MtAttachment_EcmFileId and MtAttachment_FileName columns:\n"
        "  - Only build a link when MtAttachment_EcmFileId is NOT null and NOT empty.\n"
        "  - URL pattern: https://cppapk.sharepoint.com/sites/staging/Meeting%20Sphere/{MtAttachment_EcmFileId}_{MtAttachment_FileName}\n"
        "  - If the results also contain a meeting/title column, include it in the label: 'FileName.pdf — MeetingName'\n"
        "  - Each ATTACHMENT_LINK MUST be on its own separate line. NEVER place it inline with prose text.\n"
        "  - Structure your response exactly like this:\n"
        "      <one plain intro sentence ending with a colon or period>\n"
        "      (blank line)\n"
        '      ATTACHMENT_LINK::{"url":"...","label":"..."}\n'
        '      ATTACHMENT_LINK::{"url":"...","label":"..."}\n'
        "  - No text of any kind after the last ATTACHMENT_LINK line.\n"
        "  - If MtAttachment_EcmFileId is null for a row, list the filename as plain text only — no ATTACHMENT_LINK line.\n"
        "  - Never mention EcmFileId values or technical column names to the user.\n\n"
        "STRICT RULES:\n"
        "1. Rule 1 applies ONLY when the user asks to extract, read, or get the text CONTENT "
        "from inside a file (e.g. 'read this pdf', 'show me what's written in the file'). "
        "It does NOT apply when the user is simply listing, finding, or asking about attachments. "
        "For listing/finding attachments, show the results normally.\n"
        "   When rule 1 does apply, respond with exactly: "
        "'To view this file, please wait for the upcoming version with download feature :)' "
        "— nothing else.\n"
        "2. Never mention how many rows or records were returned.\n"
        "3. Never explain technical limitations, system behavior, or what columns exist.\n"
        "4. Never suggest additional steps or workarounds.\n"
        "5. If data was found, confirm it in one plain sentence only, then list ATTACHMENT_LINK lines if applicable."
    )

def _rms_domain_block() -> str:
    """
    RMS has no attachment/status-code conventions in common with MeetingSphere.
    Extend this block as RMS-specific lookups/conventions are discovered.
    """
    return (
        "STRICT RULES:\n"
        "1. Never mention how many rows or records were returned.\n"
        "2. Never explain technical limitations, system behavior, or what columns exist.\n"
        "3. Never suggest additional steps or workarounds.\n"
        "4. If data was found, confirm it in one plain sentence only.\n"
        "5. If no data was found, say 'No matching records found.' only."
    )


def _domain_block(instance_key: str) -> str:
    if instance_key == _RMS_INSTANCE_KEY:
        return _rms_domain_block()
    return _meetingsphere_domain_block()


# ─── Natural-language summary ─────────────────────────────────────────────────

def generate_nl_summary(
    question: str,
    sql: Optional[str],
    results: Optional[list[dict]],
    error: Optional[str],
    *,
    api_key: str,
    instance_key: str = "it_meetingsphere",
    model: str = "gpt-4.1-mini",
    language: str = "English",          # "English", "Urdu", "Hinglish"
    max_sample_rows: int = 5,
) -> str:
    """
    Ask the LLM to produce a plain-language summary of the query result
    so non-technical users can understand what was returned.

    The domain-knowledge portion of the system prompt is selected based on
    instance_key, so RMS summaries don't carry MeetingSphere-specific rules
    (status codes, attachment links, etc.) that don't apply to its schema.

    The prompt is intentionally compact — we pass only a sample of the rows
    to stay within token budget and avoid leaking large result sets.
    """
    import openai
    from datetime import date

    today_str = date.today().strftime("%B %d, %Y")

    # ── Build a compact result snapshot ──────────────────────────────────────
    if error:
        result_snapshot = f"Query failed with error: {error}"
    elif not results:
        result_snapshot = "The query returned no rows."
    else:
        sample = results[:max_sample_rows]
        total  = len(results)
        rows_text = "\n".join(str(r) for r in sample)
        tail = f"\n... ({total - max_sample_rows} more rows)" if total > max_sample_rows else ""
        result_snapshot = f"Total rows returned: {total}\nSample data:\n{rows_text}{tail}"

    system_prompt = (
        f"You are a helpful assistant that explains database query results "
        f"in simple, clear {language} to non-technical users. "
        f"Today's date is {today_str}. "
        "Focus only on what directly answers the user's question.\n\n"
        f"{_domain_block(instance_key)}"
    )

    user_prompt = (
        f"A user asked: \"{question}\"\n\n"
        f"Here is the result:\n{result_snapshot}\n\n"
        "Please write a short, friendly summary explaining what this result means."
    )

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:                          # never crash the main flow
        return "Results fetched successfully."


# ─── Public query runner ──────────────────────────────────────────────────────

def run_query(instance_key: str, question: str, summary_question: Optional[str] = None) -> dict:
    """
    Normalize → Generate SQL → Validate → Execute.

    The normalization step maps user synonyms ("participants", "attendees",
    "sessions", etc.) to the canonical vocabulary used in MeetingSphere's
    training data, so Vanna's vector similarity search finds the right Q&A
    examples. This step only applies to instance_key == "it_meetingsphere";
    every other instance (including "it_rms") uses the question unchanged,
    since the normalizer's vocabulary is MeetingSphere-specific.

    Works for every instance_key, including "it_rms" — get_vanna() and
    _load_schema() already key off instance_key for connection, cache, and
    ChromaDB collection, and get_sql_prompt() picks the RMS system prompt
    automatically based on the Vanna instance's stored instance_key.

    Returns { sql, results, normalized_question, normalization_method, error }.
    """
    vn = get_vanna(instance_key)

    # ── Step 1: Normalize the question ────────────────────────────────────────
    # The synonym/rewrite map in intent_normalizer is built for MeetingSphere
    # vocabulary ("participants", "attendees", "sessions", etc.) and is not
    # relevant — and was observed to corrupt unrelated text — for other
    # instances. Skip normalization for everything except MeetingSphere.
    if instance_key == "it_meetingsphere":
        # Follow-up signal: the caller (query.py) builds `question` as the
        # context-enriched version and passes the raw question separately as
        # `summary_question`. If they differ, this turn needed prior context
        # to resolve — i.e. it's a follow-up — so let the LLM rewrite it into
        # a clean, standalone, domain-canonical question. If they're the same
        # (or no summary_question was given), it's a standalone query and we
        # skip the LLM call entirely.
        is_followup = bool(summary_question) and (
            question.strip().lower() != summary_question.strip().lower()
        )
        normalized_question, norm_method = normalize_question(
            question=question,
            api_key=settings.openai_api_key,
            is_followup=is_followup,
            model="gpt-4.1-mini",   # cheap model is fine for rewriting
        )
    else:
        normalized_question, norm_method = question, "skipped_not_meetingsphere"

    # Load and format the real schema for this instance
    schema = _load_schema(instance_key)
    schema_block = _format_schema_block(schema)

    try:
        sql = vn.generate_sql(
            question=normalized_question,   # ← normalized, not raw
            allow_llm_to_see_data=True,
            schema_constraint=schema_block,
        )

        # ── Guard: nothing returned ───────────────────────────────────────────
        if not sql:
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": "I wasn't able to understand your question well enough to search for an answer. Could you try rephrasing it?",
            }

        # ── Guard: LLM signalled no match (our NO_MATCH protocol) ────────────
        if sql.strip().startswith("NO_MATCH:"):
            user_msg = sql.strip().removeprefix("NO_MATCH:").strip()
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": user_msg,
            }

        # ── Guard: Vanna introspection blocker ────────────────────────────────
        if _INTROSPECTION_MARKER in sql:
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": "I need a moment to look that up — please try your question again.",
            }

        # ── Guard: output doesn't look like SQL ───────────────────────────────
        if not _is_valid_sql(sql):
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": "I wasn't able to find an answer for that. Try rephrasing your question.",
            }

        # ── Guard: lexical schema validation ──────────────────────────────────
        schema_error = _validate_sql_against_schema(sql, schema)
        if schema_error:
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": schema_error,
            }

        # ── Execute ───────────────────────────────────────────────────────────
        df = vn.run_sql(sql)
        if df is not None:
            # Convert nullable float-integers back to int where possible,
            # and replace NaN/NaT with None for JSON safety
            import math
            def sanitize(val):
                if val is None:
                    return None
                try:
                    import pandas as pd
                    if pd.isna(val):
                        return None
                except (TypeError, ValueError):
                    pass
                # ← Add this block:
                if isinstance(val, (bytes, bytearray)):
                    import base64
                    return base64.b64encode(val).decode('utf-8')
                if isinstance(val, float) and val.is_integer():
                    return int(val)
                return val

            results = [
                {k: sanitize(v) for k, v in record.items()}
                for record in df.to_dict(orient="records")
            ]
        else:
            results = []

        # ── Generate NL summary ───────────────────────────────────────────────
        nl_summary = generate_nl_summary(
            question=summary_question or question,   # use clean question if provided
            sql=sql,
            results=results,
            error=None,
            api_key=settings.openai_api_key,
            instance_key=instance_key,
        )

        return {
            "sql": sql,
            "results": results,
            "normalized_question": normalized_question,
            "normalization_method": norm_method,
            "nl_summary": nl_summary,
            "error": None,
        }

    except Exception as e:
        err = str(e)
        if _INTROSPECTION_MARKER in err:
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": "I need a moment to look that up — please try your question again.",
            }
        return {
            "sql": None, "results": None,
            "normalized_question": normalized_question,
            "normalization_method": norm_method,
            "nl_summary": None,
            "error": _friendly_db_error(err),
        }


# ─── Training helpers ─────────────────────────────────────────────────────────
# These already work for "it_rms" unchanged: get_vanna("it_rms") connects via
# INSTANCE_CONN_STRINGS["it_rms"] (settings.rms_connection_string), and writes
# into the isolated "vanna_it_rms" ChromaDB collection.

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