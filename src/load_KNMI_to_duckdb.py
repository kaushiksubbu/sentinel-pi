# save_weather_to_duckdb.py
import db_utils


def save_weather_to_duckdb(db_path: str, table: str, data: dict, station_id: int):
    """
    Load KNMI‑style weather data into DuckDB.
    """
    con = db_utils.connect_to_db(db_path)

    # 1. Schema for weather table
    schema = {
        "timestamp": "TIMESTAMP PRIMARY KEY",
        "station_id": "INTEGER",
        "temperature_c": "DOUBLE",
        "humidity_pct": "DOUBLE",
    }

    db_utils.create_table_if_not_exists(con, table, schema)

    # 2. Single row
    row = (
        data["timestamp"],
        station_id,
        data["temp"],
        data["hum"],
    )

    # 3. Insert
    db_utils.upsert_or_append(
        con=con,
        table=table,
        rows=[row],
        on_conflict=None,
    )

    db_utils.close_db(con)
