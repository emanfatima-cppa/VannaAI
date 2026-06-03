"""app/db/instances.py
Runtime instance registry built on top of connection_manager.
Provides:
  - health-check per instance
  - dynamic registration of new instances at runtime
  - per-instance DB type detection
  - instance summary enriched with connection status
"""
import pyodbc
import logging
from typing import Optional
from datetime import datetime

from app.db.connection_manager import (
    INSTANCE_CONN_STRINGS,
    INSTANCE_META,
    get_connection,
)

logger = logging.getLogger(__name__)

# ── DB-type → human label ─────────────────────────────────────────────────────
DB_TYPE_LABELS = {
    "sqlserver":  "SQL Server (on-prem)",
    "azure_sql":  "Azure SQL",
    "oracle":     "Oracle",
    "postgres":   "PostgreSQL",
    "mysql":      "MySQL",
}

# ── Runtime-registered extra instances (added via admin API, not in .env) ─────
_runtime_instances: dict[str, dict] = {}
_runtime_conn_strings: dict[str, str] = {}


# ── Health check ──────────────────────────────────────────────────────────────

def check_health(instance_key: str) -> dict:
    """
    Attempt a lightweight connection test.
    Returns { instance_key, healthy, latency_ms, error, checked_at }.
    """
    start = datetime.utcnow()
    try:
        conn = get_connection(instance_key)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        ms = (datetime.utcnow() - start).total_seconds() * 1000
        return {
            "instance_key": instance_key,
            "healthy": True,
            "latency_ms": round(ms, 1),
            "error": None,
            "checked_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        ms = (datetime.utcnow() - start).total_seconds() * 1000
        logger.warning(f"Health check failed for '{instance_key}': {e}")
        return {
            "instance_key": instance_key,
            "healthy": False,
            "latency_ms": round(ms, 1),
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat(),
        }


def check_all_health() -> list[dict]:
    """Run health checks for all registered instances (static + runtime)."""
    all_keys = list(INSTANCE_CONN_STRINGS.keys()) + list(_runtime_conn_strings.keys())
    return [check_health(k) for k in all_keys]


# ── Instance enrichment ───────────────────────────────────────────────────────

def get_instance_detail(instance_key: str) -> Optional[dict]:
    """
    Return merged metadata for one instance.
    Looks in static registry first, then runtime registry.
    """
    meta = INSTANCE_META.get(instance_key) or _runtime_instances.get(instance_key)
    if not meta:
        return None

    conn_str = INSTANCE_CONN_STRINGS.get(instance_key) or _runtime_conn_strings.get(instance_key)

    return {
        "key": instance_key,
        **meta,
        "db_type_label": DB_TYPE_LABELS.get(meta.get("db_type", ""), meta.get("db_type", "unknown")),
        "has_conn_string": bool(conn_str),
        "is_runtime": instance_key in _runtime_instances,
    }


def get_all_instance_details() -> list[dict]:
    """Return enriched metadata for every registered instance."""
    all_keys = list(INSTANCE_META.keys()) + list(_runtime_instances.keys())
    return [get_instance_detail(k) for k in all_keys if get_instance_detail(k)]


# ── Dynamic registration ──────────────────────────────────────────────────────

class InstanceAlreadyExistsError(Exception):
    pass


class InstanceNotFoundError(Exception):
    pass


def register_instance(
    key: str,
    label: str,
    group: str,
    db_type: str,
    description: str,
    conn_string: str,
) -> dict:
    """
    Register a new DB instance at runtime (e.g. via the admin API).
    Persists in memory only – restart will lose it unless you add it to .env / connection_manager.py.
    Raises InstanceAlreadyExistsError if the key already exists in the static registry.
    """
    if key in INSTANCE_CONN_STRINGS:
        raise InstanceAlreadyExistsError(
            f"Instance '{key}' already exists in the static registry. "
            "Edit connection_manager.py to modify it."
        )

    meta = {
        "label": label,
        "group": group,
        "db_type": db_type,
        "description": description,
    }
    _runtime_instances[key] = meta
    _runtime_conn_strings[key] = conn_string

    # Patch the live dicts so get_connection() and schema_fetcher work immediately
    INSTANCE_CONN_STRINGS[key] = conn_string
    INSTANCE_META[key] = meta

    logger.info(f"Registered new runtime instance: '{key}' ({label})")
    return get_instance_detail(key)


def deregister_instance(key: str) -> None:
    """
    Remove a runtime-registered instance.
    Static (env-backed) instances cannot be removed at runtime.
    """
    if key not in _runtime_instances:
        if key in INSTANCE_META:
            raise InstanceAlreadyExistsError(
                f"'{key}' is a static instance and cannot be removed at runtime."
            )
        raise InstanceNotFoundError(f"Instance '{key}' not found.")

    _runtime_instances.pop(key, None)
    _runtime_conn_strings.pop(key, None)
    INSTANCE_CONN_STRINGS.pop(key, None)
    INSTANCE_META.pop(key, None)
    logger.info(f"Deregistered runtime instance: '{key}'")


# ── Connection string builder helpers ─────────────────────────────────────────

def build_mssql_conn_string(
    server: str,
    database: str,
    uid: str,
    pwd: str,
    driver: str = "ODBC Driver 17 for SQL Server",
    trust_cert: bool = True,
) -> str:
    trust = "yes" if trust_cert else "no"
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        f"TrustServerCertificate={trust}"
    )


def build_azure_sql_conn_string(
    server: str,
    database: str,
    uid: str,
    pwd: str,
    driver: str = "ODBC Driver 17 for SQL Server",
    timeout: int = 30,
    command_timeout: int = 60,
) -> str:
    return (
        f"DRIVER={{{driver}}};"
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout={timeout};"
        f"Command Timeout={command_timeout}"
    )