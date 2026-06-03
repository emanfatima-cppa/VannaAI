"""
app/services/vanna_service.py
One Vanna instance per DB instance, lazily created and cached.
Uses OpenAI (GPT-5.1) as the LLM backend.
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


# ─── Custom Vanna class combining OpenAI + ChromaDB ──────────────────────────

class OpenAIVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config: dict):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)


# ─── Registry of per-instance Vanna objects ──────────────────────────────────

_instances: dict[str, OpenAIVanna] = {}
_lock = threading.Lock()


def _make_vanna(instance_key: str) -> OpenAIVanna:
    persist_path = os.path.join(settings.chroma_persist_dir, instance_key)
    os.makedirs(persist_path, exist_ok=True)

    vn = OpenAIVanna(config={
        "api_key": settings.openai_api_key,   # ✅ OpenAI key
        "model": "gpt-5.1",                   # ✅ Your required model
        "path": persist_path,
        "collection_name": f"vanna_{instance_key}",
        "allow_llm_to_see_data": True,
    })

    conn_str = INSTANCE_CONN_STRINGS[instance_key]
    vn.connect_to_mssql(odbc_conn_str=conn_str)
    return vn


def get_vanna(instance_key: str) -> OpenAIVanna:
    if instance_key not in _instances:
        with _lock:
            if instance_key not in _instances:
                _instances[instance_key] = _make_vanna(instance_key)
    return _instances[instance_key]


def _is_valid_sql(text: str) -> bool:
    if not text:
        return False
    stripped = text.strip().lstrip("(").upper()
    return bool(re.match(
        r"^(SELECT|INSERT|UPDATE|DELETE|WITH|EXEC|EXECUTE|CREATE|DROP|ALTER|MERGE)",
        stripped,
    ))


def debug_vanna(instance_key: str, question: str):
    vn = get_vanna(instance_key)

    df = vn.get_training_data()
    print("Total training records:", len(df) if df is not None else 0)
    if df is not None:
        print(df[['training_data_type', 'question', 'content']].to_string())

    similar_questions = vn.get_similar_question_sql(question)
    print("\nSimilar Q&A retrieved:", similar_questions)

    related_ddl = vn.get_related_ddl(question)
    print("\nRelated DDL retrieved:", related_ddl)

    related_docs = vn.get_related_documentation(question)
    print("\nRelated docs retrieved:", related_docs)


def run_query(instance_key: str, question: str) -> dict:
    vn = get_vanna(instance_key)
    try:
        sql = vn.generate_sql(question)

        if not sql:
            return {"sql": None, "results": None, "error": "Could not generate SQL for that question."}

        if _INTROSPECTION_MARKER in sql:
            return {
                "sql": None,
                "results": None,
                "error": (
                    "This question requires looking at actual data values to build the query. "
                    "Data introspection is enabled — please try again or rephrase."
                ),
            }

        if not _is_valid_sql(sql):
            return {
                "sql": None,
                "results": None,
                "error": f"Unexpected response instead of SQL: {sql[:200]}",
            }

        df = vn.run_sql(sql)
        results = df.to_dict(orient="records") if df is not None else []
        return {"sql": sql, "results": results, "error": None}

    except Exception as e:
        err = str(e)
        if _INTROSPECTION_MARKER in err:
            return {
                "sql": None,
                "results": None,
                "error": "Data introspection required — retry your query.",
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