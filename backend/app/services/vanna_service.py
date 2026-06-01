"""app/services/vanna_service.py
One Vanna instance per DB instance, lazily created and cached.
Uses Claude (via the Anthropic API) as the LLM backend.
"""
import os
import re
import threading
from typing import Optional

from vanna.anthropic import Anthropic_Chat
from vanna.chromadb import ChromaDB_VectorStore

from app.core.config import get_settings
from app.db.connection_manager import get_connection, INSTANCE_CONN_STRINGS

settings = get_settings()

# Vanna's exact message when it needs data introspection but the flag is off
_INTROSPECTION_MARKER = "allow_llm_to_see_data"


# ─── Custom Vanna class combining Claude + ChromaDB ──────────────────────────

class ClaudeVanna(ChromaDB_VectorStore, Anthropic_Chat):
    def __init__(self, config: dict):
        ChromaDB_VectorStore.__init__(self, config=config)
        Anthropic_Chat.__init__(self, config=config)


# ─── Registry of per-instance Vanna objects ──────────────────────────────────

_instances: dict[str, ClaudeVanna] = {}
_lock = threading.Lock()


def _make_vanna(instance_key: str) -> ClaudeVanna:
    persist_path = os.path.join(settings.chroma_persist_dir, instance_key)
    os.makedirs(persist_path, exist_ok=True)

    vn = ClaudeVanna(config={
        "api_key": settings.anthropic_api_key,
        "model": "claude-sonnet-4-6",
        "path": persist_path,
        "collection_name": f"vanna_{instance_key}",
        # ── Allow Claude to see sample data rows when needed for introspection ──
        # This is required for questions that reference specific values
        # (e.g. "show meetings for John", "find policy named X").
        # Set to False if your data is highly sensitive and you accept
        # that value-dependent questions may not work.
        "allow_llm_to_see_data": True,
    })

    # Point Vanna at the right pyodbc connection
    conn_str = INSTANCE_CONN_STRINGS[instance_key]
    vn.connect_to_mssql(odbc_conn_str=conn_str)
    return vn


def get_vanna(instance_key: str) -> ClaudeVanna:
    """Return (and cache) the Vanna instance for this DB instance."""
    if instance_key not in _instances:
        with _lock:
            if instance_key not in _instances:
                _instances[instance_key] = _make_vanna(instance_key)
    return _instances[instance_key]


def _is_valid_sql(text: str) -> bool:
    """
    Quick sanity check: the string must start with a SQL keyword.
    Catches the case where Vanna returns its own error message as 'sql'.
    """
    if not text:
        return False
    stripped = text.strip().lstrip("(").upper()
    return bool(re.match(
        r"^(SELECT|INSERT|UPDATE|DELETE|WITH|EXEC|EXECUTE|CREATE|DROP|ALTER|MERGE)",
        stripped,
    ))

def debug_vanna(instance_key: str, question: str):
    vn = get_vanna(instance_key)
    
    # 1. Check what training data exists
    df = vn.get_training_data()
    print("Total training records:", len(df) if df is not None else 0)
    if df is not None:
        print(df[['training_data_type', 'question', 'content']].to_string())
    
    # 2. Check what Vanna retrieves for this question
    similar_questions = vn.get_similar_question_sql(question)
    print("\nSimilar Q&A retrieved:", similar_questions)
    
    related_ddl = vn.get_related_ddl(question)
    print("\nRelated DDL retrieved:", related_ddl)
    
    related_docs = vn.get_related_documentation(question)
    print("\nRelated docs retrieved:", related_docs)
    
def run_query(instance_key: str, question: str) -> dict:
    """
    Generate SQL, execute it, and return structured result.
    Returns: { sql, results, error }
    """
    vn = get_vanna(instance_key)
    try:
        sql = vn.generate_sql(question)

        # ── Guard 1: nothing returned ────────────────────────────────────────
        if not sql:
            return {"sql": None, "results": None, "error": "Could not generate SQL for that question."}

        # ── Guard 2: Vanna returned its own error text instead of real SQL ───
        # This happens when allow_llm_to_see_data was False (now fixed above),
        # or if Vanna's internal flow hit another blocker.
        if _INTROSPECTION_MARKER in sql:
            return {
                "sql": None,
                "results": None,
                "error": (
                    "This question requires looking at actual data values to build the query. "
                    "Data introspection is now enabled — please try again. "
                    "If it persists, rephrase the question or add more training examples."
                ),
            }

        # ── Guard 3: output doesn't look like SQL at all ─────────────────────
        if not _is_valid_sql(sql):
            return {
                "sql": None,
                "results": None,
                "error": f"The model returned an unexpected response instead of SQL: {sql[:200]}",
            }

        df = vn.run_sql(sql)
        results = df.to_dict(orient="records") if df is not None else []
        return {"sql": sql, "results": results, "error": None}

    except Exception as e:
        err = str(e)
        # Translate the pyodbc introspection-message-as-SQL error into plain English
        if _INTROSPECTION_MARKER in err:
            return {
                "sql": None,
                "results": None,
                "error": (
                    "Data introspection was required to answer this question. "
                    "allow_llm_to_see_data is now enabled — please retry."
                ),
            }
        return {"sql": None, "results": None, "error": err}


def train_ddl(instance_key: str, ddl: str) -> None:
    vn = get_vanna(instance_key)
    vn.train(ddl=ddl)


def train_documentation(instance_key: str, doc: str) -> None:
    vn = get_vanna(instance_key)
    vn.train(documentation=doc)


def train_qa(instance_key: str, question: str, sql: str) -> None:
    vn = get_vanna(instance_key)
    vn.train(question=question, sql=sql)


def remove_training_data(instance_key: str, training_id: str) -> bool:
    vn = get_vanna(instance_key)
    return vn.remove_training_data(id=training_id)


def get_training_data(instance_key: str) -> list[dict]:
    vn = get_vanna(instance_key)
    df = vn.get_training_data()
    if df is None:
        return []
    return df.to_dict(orient="records")