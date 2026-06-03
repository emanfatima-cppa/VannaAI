"""app/db/schema_fetcher.py – auto-fetch INFORMATION_SCHEMA DDL for training."""
import pyodbc
from app.db.connection_manager import get_connection


def fetch_ddl(instance_key: str) -> list[str]:
    """
    Return a list of CREATE TABLE DDL strings built from INFORMATION_SCHEMA.
    Each string becomes one training document for Vanna.
    """
    conn = get_connection(instance_key)
    cursor = conn.cursor()

    # Get all user tables
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


def fetch_foreign_keys(instance_key: str) -> list[str]:
    """Return FK relationships as plain-English strings for training."""
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