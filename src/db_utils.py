# db_utils.py
import duckdb
import os


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


def upsert_or_append(
    con: duckdb.DuckDBPyConnection,
    table: str,
    rows: list[tuple],
    on_conflict: str = None,
):
    """
    Insert rows into table.
    rows: list of tuples matching the table columns in order.
    """
    if not rows:
        return

    n_cols = len(rows[0])
    placeholders = "(" + ", ".join("?" * n_cols) + ")"

    if on_conflict:
        query = f"INSERT INTO {table} VALUES {placeholders} ON CONFLICT {on_conflict}"
    else:
        query = f"INSERT INTO {table} VALUES {placeholders}"

    con.executemany(query, rows)


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