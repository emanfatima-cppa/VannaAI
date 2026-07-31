import pyodbc
from sqlalchemy import create_engine
from app.core.config import get_settings

settings = get_settings()

# ── Instance → raw ODBC or SQLAlchemy connection string ─────────────────────
INSTANCE_CONN_STRINGS: dict[str, str] = {
    "hr_policies":       settings.db_connection_string,
    "hr_salaries":       settings.db_connection_string,
    "it_meetingsphere":  settings.db_connection_string,
    "it_cdxp":            settings.azure_sql_connection_string,
    "it_rms":            settings.rms_connection_string,
    "it_pop":            settings.pop_connection_string,
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
        "label": "IT - Meeting Sphere Project",
        "group": "IT_docs",
        "db_type": "sqlserver",
        "description": "Meeting Sphere project database",
    },
    "it_cdxp": {
        "label": "IT – CDXP Project",
        "group": "IT_docs",
        "db_type": "azure_sql",
        "description": "Resource Management System on Azure SQL",
    },
    "it_rms": {
        "label": "IT – RMS (ECM Offline)",
        "group": "IT_docs",
        "db_type": "sqlserver",
        "description": "RMS record management database (ecmoffline_dev)",
    },
    "it_pop": {
        "label": "IT – POP (Invoices & IPPs)",
        "group": "IT_docs",
        "db_type": "oracle",
        "description": "Power Purchase & Invoice Information System (Verified/Unverified Invoices, IPP Vendors, Block & Fuel-wise data)",
    },
}


def get_connection(instance_key: str):
    """
    Return a DB connection.
    For SQL Server / Azure SQL: returns pyodbc.Connection.
    For Oracle: returns SQLAlchemy Engine Connection (oracledb).
    """
    conn_str = INSTANCE_CONN_STRINGS.get(instance_key)
    if not conn_str:
        raise ValueError(f"No connection string for instance: {instance_key}")
    
    meta = INSTANCE_META.get(instance_key, {})
    db_type = meta.get("db_type", "sqlserver")

    if db_type == "oracle":
        import oracledb
        from sqlalchemy.engine import make_url

        url = make_url(conn_str)
        username = url.username
        password = url.password
        host = url.host
        port = url.port or 1521

        service_name = url.query.get("service_name")
        sid = url.query.get("sid") or (url.database if url.database else None)

        if service_name:
            dsn = oracledb.makedsn(host, port, service_name=service_name)
        elif sid:
            dsn = oracledb.makedsn(host, port, sid=sid)
        else:
            dsn = f"{host}:{port}"

        return oracledb.connect(user=username, password=password, dsn=dsn)
    else:
        return pyodbc.connect(conn_str, timeout=30)


def get_all_instances() -> list[dict]:
    return [
        {"key": k, **v}
        for k, v in INSTANCE_META.items()
    ]