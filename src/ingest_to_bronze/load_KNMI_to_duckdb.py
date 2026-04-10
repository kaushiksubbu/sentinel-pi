# save_weather_to_duckdb.py
import db_utils
import logging
import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))


def save_weather_to_duckdb(db_path: str, table: str, data: dict, station_id: int):
    """
    Load KNMI‑style weather data into DuckDB.
    """
    con = db_utils.connect_to_db(db_path)

    # Build DICT row (not tuple)
    row = {
        "timestamp": data["timestamp"],
        "station_id": station_id,
        "temp": data["temp"],
        "hum": data["hum"],
    }

    # Use dict directly for schema inference
    inferred_schema = db_utils.infer_schema(row)
    logging.info(f"Inferred schema for KNMI: {inferred_schema}")

    # Create table if needed
    db_utils.create_table_if_not_exists(con, table, inferred_schema)

    # Insert single row (list with 1 dict)
    db_utils.upsert_or_append(
        con=con,
        table=table,
        rows=[row],  # List of dicts
        on_conflict=None,
    )

    db_utils.close_db(con)
    logging.info(f"Saved KNMI weather data for station {station_id}")
