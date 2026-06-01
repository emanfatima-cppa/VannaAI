"""app/db/connection_manager.py – pyodbc connections per instance."""
import pyodbc
from app.core.config import get_settings

settings = get_settings()

# ── Instance → raw ODBC connection string ────────────────────────────────────
INSTANCE_CONN_STRINGS: dict[str, str] = {
    "hr_policies":       settings.db_connection_string,
    "hr_salaries":       settings.db_connection_string,
    "it_meetingsphere":  settings.db_connection_string,
    "it_cdxp":            settings.azure_sql_connection_string,
}

# ── Instance → human readable metadata ───────────────────────────────────────
INSTANCE_META: dict[str, dict] = {
    "hr_policies": {
        "label": "HR – Policies",
        "group": "hr_docs",
        "db_type": "sqlserver",
        "description": "Company policy documents and HR guidelines",
    },
    "hr_salaries": {
        "label": "HR – Salaries",
        "group": "hr_docs",
        "db_type": "sqlserver",
        "description": "Salary bands, compensation data",
    },
    "it_meetingsphere": {
        "label": "IT – MeetingSphere Project",
        "group": "IT_docs",
        "db_type": "sqlserver",
        "description": "MeetingSphere project database",
    },
    "it_cdxp": {
        "label": "IT – CDXP Project",
        "group": "IT_docs",
        "db_type": "azure_sql",
        "description": "Resource Management System on Azure SQL",
    },
}


def get_connection(instance_key: str) -> pyodbc.Connection:
    conn_str = INSTANCE_CONN_STRINGS.get(instance_key)
    if not conn_str:
        raise ValueError(f"No connection string for instance: {instance_key}")
    return pyodbc.connect(conn_str, timeout=30)


def get_all_instances() -> list[dict]:
    return [
        {"key": k, **v}
        for k, v in INSTANCE_META.items()
    ]