# transform_zigbee_to_silver.py

from contracts import ZIGBEE_CONTRACT
from metrics_contract import SilverMetrics
from pipeline_logger import write_jsonl_entry
from datetime import datetime, timezone
from db_utils import connect_to_db, close_db, create_table_with_ddl
from config import BRONZE_DB, SILVER_DB, OPS_DB
from openlineage_emitter import emit_lineage_event, get_run_id

import logging
import duckdb
import json

import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))


def extract_by_contract(data: dict, concept: str) -> float:
    """
    Extracts value using known aliases from contract.
    Logs warning if unknown alias detected.
    Returns None if no match found.
    """
    aliases = ZIGBEE_CONTRACT.get(concept, [])
    value = next((data[k] for k in aliases if k in data), None)

    if value is None:
        unknown = [k for k in data if concept[:3] in k.lower()]
        if unknown:
            logging.warning(
                f"Unknown alias for {concept}: {unknown} — update contracts.py"
            )
    return value


CREATE_WATERMARKS = """
    CREATE TABLE IF NOT EXISTS watermarks (
        source          VARCHAR,
        last_processed  TIMESTAMP,
        updated_at      TIMESTAMP,
        PRIMARY KEY (source)
    )
"""


def get_watermark(ops_con, source: str) -> datetime:
    """
    Returns last processed timestamp for source.
    Returns 0001-01-01 if no watermark exists.
    """
    result = ops_con.execute("""
        SELECT last_processed
        FROM watermarks
        WHERE source = ?
    """, [source]).fetchone()

    if result is None:
        return datetime(1, 1, 1)  # 0001-01-01
    return result[0]


def update_watermark(ops_con, source: str, timestamp: datetime):
    """
    Updates watermark for source after successful transform.
    """
    ops_con.execute("""
        INSERT OR REPLACE INTO watermarks
        (source, last_processed, updated_at)
        VALUES (?, ?, ?)
    """, [
        source,
        timestamp,
        datetime.now(timezone.utc)
    ])


def read_zigbee_bronze(
    bronze_con: duckdb.DuckDBPyConnection,
    watermark: datetime,
) -> list[tuple]:
    """
    Reads unprocessed Zigbee Bronze rows.
    Excludes Bath — internally driven microclimate.
    Returns rows ordered by timestamp ASC.
    Single responsibility: fetch only.
    """
    return bronze_con.execute("""
        SELECT
            timestamp,
            topic,
            payload,
            source_file
        FROM zigbee_raw
        WHERE timestamp > ?
        AND topic NOT LIKE '%Bath%'
        ORDER BY timestamp ASC
    """, [watermark]).fetchall()


def validate_zigbee_row(
    temp: float,
    humidity: float,
) -> tuple[bool, str]:
    """
    Validates Zigbee indoor temp and humidity.
    Returns (is_valid, dq_flag).
    indoor_temp:     14 to 30
    indoor_humidity: 25 to 85
    rh prefix aligns with KNMI DQ standard across Silver.
    """
    flags = []

    if temp is None:
        flags.append("temp_null")
    elif temp < 14 or temp > 30:
        flags.append("temp_out_of_range")

    if humidity is None:
        flags.append("rh_null")
    elif humidity < 25 or humidity > 85:
        flags.append("rh_out_of_range")

    is_valid = len(flags) == 0
    dq_flag = "|".join(flags) if flags else None

    return is_valid, dq_flag


def write_zigbee_silver(
    silver_con: duckdb.DuckDBPyConnection,
    ops_con: duckdb.DuckDBPyConnection,
    silver_rows: list[tuple],
    bronze_rows: list[tuple],
) -> dict:
    """
    Writes Zigbee Silver rows to weather_silver.
    Updates watermark only after successful write.
    Returns observability counts.
    Single responsibility: write only.
    """
    silver_con.executemany("""
        INSERT OR IGNORE INTO weather_silver
        (observed_at, location, data_provider,
         temp, humidity, wind_speed,
         is_valid, dq_flag, source_file, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, silver_rows)

    max_observed_at = max(row[0] for row in bronze_rows)
    update_watermark(ops_con, 'zigbee', max_observed_at)

    valid_count = sum(1 for row in silver_rows if row[6] is True)
    invalid_count = sum(1 for row in silver_rows if row[6] is False)

    return {
        "total": len(silver_rows),
        "valid": valid_count,
        "invalid": invalid_count,
        "watermark": max_observed_at,
    }


def validate_zigbee_rows(
    bronze_rows: list[tuple],
) -> list[tuple]:
    """
    Validates Zigbee Bronze rows.
    Parses JSON payload.
    Extracts location from topic.
    Returns Silver-ready rows — ALL rows, valid and invalid.
    Single responsibility: DQ only.
    """
    silver_rows = []

    for row in bronze_rows:
        timestamp, topic, payload, source_file = row

        # Extract location from topic
        location = topic.split("/")[1].split(" ")[0]

        # Parse payload
        data = json.loads(payload)
        temp = extract_by_contract(data, "temperature")
        humidity = extract_by_contract(data, "humidity")

        # Validate
        is_valid, dq_flag = validate_zigbee_row(temp, humidity)

        silver_rows.append((
            timestamp,      # observed_at
            location,       # location
            'zigbee',       # data_provider
            temp,           # temp
            humidity,       # humidity
            None,           # wind_speed — structural NULL
            is_valid,       # is_valid
            dq_flag,        # dq_flag
            source_file,    # source_file
            datetime.now(timezone.utc),  # processed_at
        ))

    return silver_rows


def transform_zigbee_to_silver():
    """
    Orchestrates Zigbee Bronze → Silver transformation.
    Reads → Validates → Writes.
    Excludes Bath at read stage.
    """
    start_time = datetime.now(timezone.utc)
    run_id = get_run_id()          # added as a part of Openlineage
    bronze_con = None
    silver_con = None
    ops_con = None

    try:
        bronze_con = connect_to_db(BRONZE_DB)
        silver_con = connect_to_db(SILVER_DB)
        ops_con = connect_to_db(OPS_DB)

        create_table_with_ddl(ops_con, CREATE_WATERMARKS)

        emit_lineage_event(
            job_name="transform_zigbee_silver",
            run_id=run_id,
            state="START",
            inputs=["bronze.zigbee_raw"],
            outputs=["silver.weather_silver"]
        )

        # Step 1 — Read
        watermark = get_watermark(ops_con, 'zigbee')
        bronze_rows = read_zigbee_bronze(bronze_con, watermark)

        if not bronze_rows:
            logging.info("Zigbee Silver | No new rows.")
            return

        # Step 2 — Validate
        silver_rows = validate_zigbee_rows(bronze_rows)

        # Step 3 — Write
        result = write_zigbee_silver(
            silver_con, ops_con, silver_rows, bronze_rows
        )

        logging.info(
            f"Zigbee Silver | "
            f"Total: {result['total']} | "
            f"Valid: {result['valid']} | "
            f"Invalid: {result['invalid']} | "
            f"Watermark: {result['watermark']}"
        )

        emit_lineage_event(
            job_name="transform_zigbee_silver",
            run_id=run_id,
            state="COMPLETE",
            inputs=["bronze.zigbee_raw"],
            outputs=["silver.weather_silver"]
        )

        write_jsonl_entry(
            stage="transform_zigbee_silver",
            status="success",
            start_time=start_time,
            metrics=SilverMetrics(
                records_in=result['total'],
                records_out=result['valid'],
                dq_pass_rate=round(result['valid'] / result['total'] * 100, 1)
                if result['total'] > 0 else 0.0
            )
        )

    except Exception as e:
        logging.error(f"Zigbee Silver | Transform failed | {e}")
        emit_lineage_event(
            job_name="transform_zigbee_silver",
            run_id=run_id,
            state="FAIL",
            inputs=["bronze.zigbee_raw"],
            outputs=["silver.weather_silver"]
        )
        write_jsonl_entry(
            stage="transform_zigbee_silver",
            status="error",
            start_time=start_time,
            error=str(e)
        )
        raise

    finally:
        if bronze_con:
            close_db(bronze_con)
        if silver_con:
            close_db(silver_con)
        if ops_con:
            close_db(ops_con)


if __name__ == "__main__":
    transform_zigbee_to_silver()
