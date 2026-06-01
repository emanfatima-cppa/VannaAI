"""app/training/trainer.py
Bootstrap training for all (or a specific) instance.
Fetches INFORMATION_SCHEMA DDL automatically, then adds dummy Q&A pairs.
"""
import logging
from app.db.schema_fetcher import fetch_ddl, fetch_foreign_keys
from app.services.vanna_service import train_ddl, train_documentation, train_qa
from app.training.dummy_data import DUMMY_TRAINING

logger = logging.getLogger(__name__)


def train_instance(instance_key: str, skip_schema: bool = False) -> dict:
    """
    Full training pipeline for one DB instance:
    1. Fetch & train DDL from INFORMATION_SCHEMA
    2. Train FK documentation strings
    3. Train dummy Q&A pairs and documentation
    Returns a summary dict.
    """
    summary = {"instance": instance_key, "ddl": 0, "fk_docs": 0, "qa": 0, "docs": 0, "errors": []}

    # ── 1. Schema from INFORMATION_SCHEMA ────────────────────────────────────
    if not skip_schema:
        try:
            ddl_list = fetch_ddl(instance_key)
            for ddl in ddl_list:
                train_ddl(instance_key, ddl)
            summary["ddl"] = len(ddl_list)
            logger.info(f"[{instance_key}] Trained {len(ddl_list)} DDL statements")
        except Exception as e:
            msg = f"DDL fetch error: {e}"
            summary["errors"].append(msg)
            logger.error(f"[{instance_key}] {msg}")

        try:
            fk_docs = fetch_foreign_keys(instance_key)
            for doc in fk_docs:
                train_documentation(instance_key, doc)
            summary["fk_docs"] = len(fk_docs)
        except Exception as e:
            msg = f"FK doc error: {e}"
            summary["errors"].append(msg)
            logger.error(f"[{instance_key}] {msg}")

    # ── 2. Dummy / seed training data ─────────────────────────────────────────
    seed = DUMMY_TRAINING.get(instance_key, {})

    for doc in seed.get("documentation", []):
        try:
            train_documentation(instance_key, doc)
            summary["docs"] += 1
        except Exception as e:
            summary["errors"].append(f"doc: {e}")

    for pair in seed.get("qa_pairs", []):
        try:
            train_qa(instance_key, pair["question"], pair["sql"])
            summary["qa"] += 1
        except Exception as e:
            summary["errors"].append(f"qa: {e}")

    return summary


def train_all_instances(skip_schema: bool = False) -> list[dict]:
    from app.db.connection_manager import INSTANCE_CONN_STRINGS
    results = []
    for key in INSTANCE_CONN_STRINGS:
        results.append(train_instance(key, skip_schema=skip_schema))
    return results