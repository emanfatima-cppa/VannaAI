"""app/db/schema_fetcher.py – auto-fetch DDL for training (SQL Server & Oracle)."""
import logging
from sqlalchemy import text
from app.db.connection_manager import get_connection, INSTANCE_META

logger = logging.getLogger(__name__)


def fetch_ddl(instance_key: str) -> list[str]:
    """
    Return a list of CREATE TABLE DDL strings built from database dictionary metadata.
    Supports SQL Server / Azure SQL (via pyodbc + INFORMATION_SCHEMA)
    and Oracle DB (via sqlalchemy/oracledb + USER_TABLES / USER_TAB_COLUMNS).
    """
    meta = INSTANCE_META.get(instance_key, {})
    db_type = meta.get("db_type", "sqlserver")

    if db_type == "oracle":
        return _fetch_ddl_oracle(instance_key)
    else:
        return _fetch_ddl_sqlserver(instance_key)


def fetch_foreign_keys(instance_key: str) -> list[str]:
    """Return FK relationships as plain-English strings for training."""
    meta = INSTANCE_META.get(instance_key, {})
    db_type = meta.get("db_type", "sqlserver")

    if db_type == "oracle":
        return _fetch_fk_oracle(instance_key)
    else:
        return _fetch_fk_sqlserver(instance_key)


# ── SQL Server Implementation ──────────────────────────────────────────────────

def _fetch_ddl_sqlserver(instance_key: str) -> list[str]:
    conn = get_connection(instance_key)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    tables = cursor.fetchall()

    ddl_statements = []
    for schema, table in tables:
        cursor.execute("""
            SELECT
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.CHARACTER_MAXIMUM_LENGTH,
                c.IS_NULLABLE,
                c.COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS c
            WHERE c.TABLE_SCHEMA = ? AND c.TABLE_NAME = ?
            ORDER BY c.ORDINAL_POSITION
        """, schema, table)
        columns = cursor.fetchall()

        col_defs = []
        for col in columns:
            col_name, data_type, max_len, nullable, default = col
            type_str = data_type
            if max_len:
                type_str += f"({max_len})"
            null_str = "NULL" if nullable == "YES" else "NOT NULL"
            col_defs.append(f"    {col_name} {type_str} {null_str}")

        ddl = f"CREATE TABLE [{schema}].[{table}] (\n"
        ddl += ",\n".join(col_defs)
        ddl += "\n);"
        ddl_statements.append(ddl)

    conn.close()
    return ddl_statements


def _fetch_fk_sqlserver(instance_key: str) -> list[str]:
    conn = get_connection(instance_key)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            fk.name AS fk_name,
            tp.name AS parent_table,
            cp.name AS parent_col,
            tr.name AS ref_table,
            cr.name AS ref_col
        FROM sys.foreign_keys fk
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
        JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
        JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
        JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
    """)
    rows = cursor.fetchall()
    conn.close()

    docs = []
    for row in rows:
        _, parent_table, parent_col, ref_table, ref_col = row
        docs.append(
            f"The column [{parent_table}].[{parent_col}] references [{ref_table}].[{ref_col}]."
        )
    return docs


# ── Oracle Implementation ──────────────────────────────────────────────────────

def _fetch_ddl_oracle(instance_key: str) -> list[str]:
    conn = get_connection(instance_key)
    ddl_statements = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT OWNER, TABLE_NAME 
            FROM ALL_TABLES 
            WHERE OWNER NOT IN ('SYS', 'SYSTEM', 'AUDSYS', 'OUTLN', 'DBSNMP', 'XDB', 'GSMADMIN_INTERNAL', 'CTXSYS', 'MDSYS', 'WMSYS', 'OJVMSYS', 'LBACSYS', 'ORDSYS', 'ORDDATA')
              AND OWNER NOT LIKE 'APEX%'
            ORDER BY OWNER, TABLE_NAME
        """)
        tables = cursor.fetchall()

        for owner, table in tables:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, DATA_SCALE, NULLABLE
                FROM ALL_TAB_COLUMNS
                WHERE OWNER = :1 AND TABLE_NAME = :2
                ORDER BY COLUMN_ID
            """, [owner, table])
            columns = cursor.fetchall()

            col_defs = []
            for col in columns:
                col_name, data_type, data_len, data_prec, data_scale, nullable = col
                if data_type in ('VARCHAR2', 'CHAR', 'NVARCHAR2'):
                    type_str = f"{data_type}({data_len})"
                elif data_type == 'NUMBER' and data_prec is not None:
                    if data_scale:
                        type_str = f"NUMBER({data_prec},{data_scale})"
                    else:
                        type_str = f"NUMBER({data_prec})"
                else:
                    type_str = data_type
                
                null_str = "NULL" if nullable == "Y" else "NOT NULL"
                col_defs.append(f"    {col_name} {type_str} {null_str}")

            ddl = f"CREATE TABLE {owner}.{table} (\n"
            ddl += ",\n".join(col_defs)
            ddl += "\n);"
            ddl_statements.append(ddl)
    finally:
        conn.close()

    return ddl_statements


def _fetch_fk_oracle(instance_key: str) -> list[str]:
    conn = get_connection(instance_key)
    docs = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.owner AS parent_owner,
                a.table_name AS parent_table,
                a.column_name AS parent_col,
                c_pk.owner AS ref_owner,
                c_pk.table_name AS ref_table,
                b.column_name AS ref_col
            FROM all_cons_columns a
            JOIN all_constraints c ON a.owner = c.owner AND a.constraint_name = c.constraint_name
            JOIN all_constraints c_pk ON c.r_owner = c_pk.owner AND c.r_constraint_name = c_pk.constraint_name
            JOIN all_cons_columns b ON c_pk.owner = b.owner AND c_pk.constraint_name = b.constraint_name AND a.position = b.position
            WHERE c.constraint_type = 'R'
              AND a.owner NOT IN ('SYS', 'SYSTEM', 'AUDSYS', 'OUTLN', 'DBSNMP', 'XDB', 'GSMADMIN_INTERNAL', 'CTXSYS', 'MDSYS', 'WMSYS')
              AND a.owner NOT LIKE 'APEX%'
        """)
        rows = cursor.fetchall()
        for row in rows:
            p_owner, parent_table, parent_col, r_owner, ref_table, ref_col = row
            docs.append(
                f"The column {p_owner}.{parent_table}.{parent_col} references {r_owner}.{ref_table}.{ref_col}."
            )
    finally:
        conn.close()

    return docs