# db_utils.py
import duckdb
import os
import datetime
import logging


def ensure_db_dir(db_path: str):
    """Ensure parent directory of db_path exists."""
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


def connect_to_db(db_path: str) -> duckdb.DuckDBPyConnection:
    """Open a connection to DuckDB and ensure db_dir exists."""
    ensure_db_dir(db_path)
    return duckdb.connect(db_path)


def close_db(con: duckdb.DuckDBPyConnection):
    """Close the DuckDB connection."""
    con.close()


def create_table_if_not_exists(
    con: duckdb.DuckDBPyConnection,
    table: str,
    schema: dict,
):
    """
    Create table with given schema if it doesn't exist.
    schema: dict of col_name -> type (string).
    Example:
        schema = {"timestamp": "TIMESTAMP", "topic": "VARCHAR", "payload": "JSON"}
    """
    cols = ", ".join(f"{name} {type_}" for name, type_ in schema.items())
    query = f"CREATE TABLE IF NOT EXISTS {table} ({cols})"
    con.execute(query)


def upsert_or_append(con, table: str, rows: list, on_conflict=None):
    if not rows:
        return
    
    # Handle both dicts and tuples
    processed_rows = []
    for row in rows:
        if isinstance(row, dict):
            # Convert dict to tuple using schema order
            columns = list(row.keys())
            processed_rows.append(tuple(row[col] for col in columns))
        else:
            # Already tuple
            processed_rows.append(row)
    
    columns = list(rows[0].keys()) if isinstance(rows[0], dict) else None
    placeholders = ', '.join(['?' for _ in processed_rows[0]])
    query = f"INSERT INTO {table} VALUES ({placeholders})"
    
    con.executemany(query, processed_rows)

def read_query(
    db_path: str,
    sql: str,
    params: tuple = None,
) -> list[dict]:
    """
    Execute a SELECT query and return result as a list of dicts (row → dict).
    """
    con = connect_to_db(db_path)
    try:
        if params:
            result = con.execute(sql, params)
        else:
            result = con.execute(sql)

        # List of dicts, one per row
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()

        return [dict(zip(columns, row)) for row in rows]
    finally:
        close_db(con)


def read_table(
    db_path: str,
    table: str,
    limit: int = None,
) -> list[dict]:
    """
    Read a full table (or first N rows) into a list of dicts.
    """
    sql = f"SELECT * FROM {table}"
    if limit:
        sql += f" LIMIT {limit}"

    return read_query(db_path, sql)

def infer_schema(sample_row: dict) -> dict:
    """Dynamically infer DuckDB column types - NO IMPORTS NEEDED 
    WARNING: Prototype use only - Donot use for Bronze or Silver table creation.
    Schema must be explicit in production layers.
    """
    schema = {}
    
    for col, value in sample_row.items():
        value_type = type(value).__name__
        
        if value is None or value == "":
            schema[col] = "VARCHAR"
        elif value_type == 'str':
            schema[col] = "VARCHAR"
        elif value_type == 'datetime':
            schema[col] = "TIMESTAMP"
        elif value_type in ('int', 'float'):
            schema[col] = "DOUBLE"
        elif value_type == 'bool':
            schema[col] = "BOOLEAN"
        else:
            schema[col] = "VARCHAR"
    
    return schema

def create_table_with_ddl(
    con: duckdb.DuckDBPyConnection,
    ddl: str,
    ):
    """
    Creates table using raw DDL string.
    Use when schema requires PRIMARY KEY, 
    constraints, or complex column definitions.
    Simple schemas use create_table_if_not_exists instead.
    """
    con.execute(ddl)

def bulk_insert_ignore(
    con: duckdb.DuckDBPyConnection,
    table: str,
    rows: list,
) -> dict:
    """
    Bulk insert rows using INSERT OR IGNORE.
    Counts attempted, inserted, and duplicate rows.
    Returns dict with counts for logging and observability.
    """
    if not rows:
        return {"attempted": 0, "inserted": 0, "duplicates": 0}

    columns = list(rows[0].keys())
    placeholders = ", ".join(["?" for _ in columns])
    col_names = ", ".join(columns)

    insert_sql = f"""
        INSERT OR IGNORE INTO {table} ({col_names})
        VALUES ({placeholders})
    """

    tuples = [tuple(row[c] for c in columns) for row in rows]
    
    # Count before insert
    count_before = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]
    
    con.executemany(insert_sql, tuples)
    
    # Count after insert
    count_after = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    attempted  = len(tuples)
    inserted   = count_after - count_before
    duplicates = attempted - inserted

    return {
        "attempted":  attempted,
        "inserted":   inserted,
        "duplicates": duplicates,
    }

def connect_to_db_readonly(db_path: str):
    """
    Read-only connection — safe for queries during pipeline runs.
    Use for: AI scripts, manual queries, reporting.
    Never use for: Bronze/Silver/Gold writes.
    """
    return duckdb.connect(db_path, read_only=True)