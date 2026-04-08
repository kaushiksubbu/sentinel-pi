# transform_knmi_to_silver.py

from metrics_contract import SilverMetrics
from pipeline_logger import write_jsonl_entry
from datetime import datetime, timezone
from db_utils import connect_to_db, close_db, create_table_with_ddl
from config import BRONZE_DB, SILVER_DB, OPS_DB
from openlineage_emitter import emit_lineage_event, get_run_id
import logging
import duckdb
import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))


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


def validate_knmi_row(ta: float, rh: float) -> tuple[bool, str]:
    flags = []
    if ta is None:
        flags.append("ta_null")
    elif ta < -25 or ta > 45:
        flags.append("ta_out_of_range")
    if rh is None:
        flags.append("rh_null")
    elif rh < 40 or rh > 100:
        flags.append("rh_out_of_range")
    is_valid = len(flags) == 0
    dq_flag = "|".join(flags) if flags else None
    return is_valid, dq_flag


def read_knmi_bronze(
    bronze_con: duckdb.DuckDBPyConnection,
    watermark: datetime,
) -> list[tuple]:
    """
    Reads unprocessed KNMI Bronze rows.
    Returns raw rows ordered by observed_at ASC.
    No validation. No transformation.
    Single responsibility: fetch only.
    """
    return bronze_con.execute("""
        SELECT
            observed_at,
            stationname,
            ta,
            rh,
            ff,
            source_file
        FROM knmi_raw
        WHERE observed_at > ?
        ORDER BY observed_at ASC
    """, [watermark]).fetchall()


def write_knmi_silver(
    silver_con: duckdb.DuckDBPyConnection,
    ops_con: duckdb.DuckDBPyConnection,
    silver_rows: list[tuple],
    bronze_rows: list[tuple],
) -> dict:
    """
    Writes Silver rows to weather_silver.
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

    # Update watermark
    max_observed_at = max(row[0] for row in bronze_rows)
    update_watermark(ops_con, 'knmi', max_observed_at)

    valid_count = sum(1 for row in silver_rows if row[6] is True)
    invalid_count = sum(1 for row in silver_rows if row[6] is False)

    return {
        "total": len(silver_rows),
        "valid": valid_count,
        "invalid": invalid_count,
        "watermark": max_observed_at,
    }


def validate_knmi_rows(
    bronze_rows: list[tuple],
) -> list[tuple]:
    """
    Validates Bronze rows.
    Returns Silver-ready rows — ALL rows, valid and invalid.
    Never drops a row.
    Single responsibility: DQ only.
    """
    silver_rows = []
    for row in bronze_rows:
        observed_at, stationname, ta, rh, ff, source_file = row
        is_valid, dq_flag = validate_knmi_row(ta, rh)
        silver_rows.append((
            observed_at,
            stationname,
            'knmi',
            ta,
            rh,
            ff,
            is_valid,
            dq_flag,
            source_file,
            datetime.now(timezone.utc),
        ))
    return silver_rows


def transform_knmi_to_silver():
    """
    Orchestrates Bronze → Silver transformation.
    Reads → Validates → Writes.
    Each step independently responsible.
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

        # Open Lineage set up
        emit_lineage_event(
            job_name="transform_knmi_silver",
            run_id=run_id,
            state="START",
            inputs=["bronze.knmi_raw"],
            outputs=["silver.weather_silver"]
        )

        # Step 1 — Read
        watermark = get_watermark(ops_con, 'knmi')
        bronze_rows = read_knmi_bronze(bronze_con, watermark)

        if not bronze_rows:
            logging.info("KNMI Silver | No new rows.")
            return

        # Step 2 — Validate
        silver_rows = validate_knmi_rows(bronze_rows)

        # Step 3 — Write
        result = write_knmi_silver(
            silver_con, ops_con, silver_rows, bronze_rows
        )

        logging.info(
            f"KNMI Silver | "
            f"Total: {result['total']} | "
            f"Valid: {result['valid']} | "
            f"Invalid: {result['invalid']} | "
            f"Watermark: {result['watermark']}"
        )

        # Open Lineage set up
        emit_lineage_event(
            job_name="transform_knmi_silver",
            run_id=run_id,
            state="COMPLETE",
            inputs=["bronze.knmi_raw"],
            outputs=["silver.weather_silver"]
        )

        write_jsonl_entry(
            stage="transform_knmi_silver",
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
        logging.error(f"KNMI Silver | Transform failed | {e}")
        emit_lineage_event(
            job_name="transform_knmi_silver",
            run_id=run_id,
            state="FAIL",
            inputs=["bronze.knmi_raw"],
            outputs=["silver.weather_silver"]
        )
        write_jsonl_entry(
            stage="transform_knmi_silver",
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
    transform_knmi_to_silver()
