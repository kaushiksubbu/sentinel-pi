# transform_silver_to_gold.py
#
# ARCHITECTURE NOTE:
# Functions here are modular by design — not yet microservices.
# read_silver_for_gold, aggregate_to_gold, write_gold
# are independently testable modules today.
# Phase 2: each function becomes its own Docker container
# orchestrated via Docker Compose.
# This code requires no rewrite for that migration.

from datetime import datetime, timezone, timedelta
import duckdb
import logging

from db_utils import connect_to_db, close_db, create_table_with_ddl
from config import SILVER_DB, GOLD_DB, OPS_DB, KNMI_COMPLETENESS_MIN, ZIGBEE_COMPLETENESS_MIN

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


def read_silver_for_gold(
    silver_con: duckdb.DuckDBPyConnection,
    watermark: datetime,
) -> tuple[list, list]:
    """
    Reads Silver rows for Gold aggregation.
    Aggregates KNMI and Zigbee to hourly windows independently.
    Only reads valid rows — Gold built on clean data only.
    Single responsibility: fetch only.
    """
    knmi_rows = silver_con.execute("""
            SELECT
                DATE_TRUNC('hour', observed_at)          AS window_start,
                location                                  AS outdoor_location,
                AVG(temp)                                 AS avg_outdoor_temp,
                AVG(humidity)                             AS avg_outdoor_humidity,
                AVG(wind_speed)                           AS avg_wind_speed,
                COUNT(*) FILTER (WHERE is_valid = TRUE)   AS knmi_valid_count,
                COUNT(*)                                  AS knmi_total_count
            FROM weather_silver
            WHERE data_provider = 'knmi'
            AND observed_at > ?
            AND DATE_TRUNC('hour', observed_at) + INTERVAL '1 hour' < NOW()
            GROUP BY DATE_TRUNC('hour', observed_at), location
        """, [watermark]).fetchall()

    zigbee_rows = silver_con.execute("""
            SELECT
                DATE_TRUNC('hour', observed_at)          AS window_start,
                location                                  AS indoor_location,
                AVG(temp)                                 AS avg_indoor_temp,
                AVG(humidity)                             AS avg_indoor_humidity,
                COUNT(*) FILTER (WHERE is_valid = TRUE)   AS zigbee_valid_count,
                COUNT(*)                                  AS zigbee_total_count
            FROM weather_silver
            WHERE data_provider = 'zigbee'
            AND observed_at > ?
            AND DATE_TRUNC('hour', observed_at) + INTERVAL '1 hour' < NOW()
            GROUP BY DATE_TRUNC('hour', observed_at), location
            """, [watermark]).fetchall()

    logging.info(
        f"Gold | Read Silver | "
        f"KNMI hourly windows: {len(knmi_rows)} | "
        f"Zigbee hourly windows: {len(zigbee_rows)}"
    )

    return knmi_rows, zigbee_rows


def aggregate_to_gold(
    knmi_rows: list[tuple],
    zigbee_rows: list[tuple],
) -> list[tuple]:
    """
    Joins KNMI and Zigbee hourly aggregations.
    Produces 8 rows per complete hour (2 outdoor x 4 indoor).
    Applies DQ thresholds.
    Single responsibility: aggregation logic only.
    """
    gold_rows = []

    for knmi in knmi_rows:
        window_start, outdoor_location, \
        avg_outdoor_temp, avg_outdoor_humidity, \
        avg_wind_speed, knmi_valid_count, knmi_total_count = knmi

        window_end = window_start + timedelta(hours=1)

        for zigbee in zigbee_rows:
            z_window_start, indoor_location, \
            avg_indoor_temp, avg_indoor_humidity, \
            zigbee_valid_count, zigbee_total_count = zigbee

            # Only join matching hours
            if z_window_start != window_start:
                continue

            # DQ validation
            flags = []

            knmi_completeness   = knmi_valid_count / knmi_total_count \
                                if knmi_total_count > 0 else 0
            zigbee_completeness = zigbee_valid_count / zigbee_total_count \
                                if zigbee_total_count > 0 else 0

            if knmi_completeness < KNMI_COMPLETENESS_MIN:
                flags.append("knmi_low_completeness")
            if zigbee_completeness < ZIGBEE_COMPLETENESS_MIN:
                flags.append("zigbee_low_completeness")

            is_valid = len(flags) == 0
            dq_flag  = "|".join(flags) if flags else None

            gold_rows.append((
                window_start,           # window_start
                window_end,             # window_end
                outdoor_location,       # outdoor_location
                indoor_location,        # indoor_location
                avg_outdoor_temp,       # avg_outdoor_temp
                avg_outdoor_humidity,   # avg_outdoor_humidity
                avg_wind_speed,         # avg_wind_speed
                avg_indoor_temp,        # avg_indoor_temp
                avg_indoor_humidity,    # avg_indoor_humidity
                knmi_valid_count,       # knmi_valid_count
                zigbee_valid_count,     # zigbee_valid_count
                is_valid,               # is_valid       [index 11]
                dq_flag,                # dq_flag        [index 12]
                datetime.now(timezone.utc),  # processed_at  [index 13]
            ))

    return gold_rows


def write_gold(
    gold_con: duckdb.DuckDBPyConnection,
    ops_con: duckdb.DuckDBPyConnection,
    gold_rows: list[tuple],
) -> dict:
    """
    Writes Gold rows to gold_weather.
    Updates watermark only after successful write.
    Returns observability counts.
    Single responsibility: write only.
    """
    gold_con.executemany("""
        INSERT OR IGNORE INTO gold_weather
        (window_start, window_end,
         outdoor_location, indoor_location,
         avg_outdoor_temp, avg_outdoor_humidity, avg_wind_speed,
         avg_indoor_temp, avg_indoor_humidity,
         knmi_valid_count, zigbee_valid_count,
         is_valid, dq_flag, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, gold_rows)

    max_window_start = max(row[0] for row in gold_rows)
    update_watermark(ops_con, 'gold_weather', max_window_start)

    valid_count   = sum(1 for row in gold_rows if row[11] is True)
    invalid_count = sum(1 for row in gold_rows if row[11] is False)

    return {
        "total":     len(gold_rows),
        "valid":     valid_count,
        "invalid":   invalid_count,
        "watermark": max_window_start,
    }


def transform_silver_to_gold():
    """
    Orchestrates Silver → Gold transformation.
    Reads → Aggregates → Writes.
    Each step independently responsible.
    """
    silver_con = None
    gold_con   = None
    ops_con    = None

    try:
        silver_con = connect_to_db(SILVER_DB)
        gold_con   = connect_to_db(GOLD_DB)
        ops_con    = connect_to_db(OPS_DB)

        create_table_with_ddl(ops_con, CREATE_WATERMARKS)

        # Step 1 — Read
        watermark = get_watermark(ops_con, 'gold_weather')
        knmi_rows, zigbee_rows = read_silver_for_gold(
            silver_con, watermark
        )

        if not knmi_rows or not zigbee_rows:
            logging.info("Gold | No new Silver rows to aggregate.")
            return

        # Step 2 — Aggregate
        gold_rows = aggregate_to_gold(knmi_rows, zigbee_rows)

        if not gold_rows:
            logging.info("Gold | No complete hours to aggregate.")
            return

        # Step 3 — Write
        result = write_gold(gold_con, ops_con, gold_rows)

        logging.info(
            f"Gold | "
            f"Total: {result['total']} | "
            f"Valid: {result['valid']} | "
            f"Invalid: {result['invalid']} | "
            f"Watermark: {result['watermark']}"
        )

    except Exception as e:
        logging.error(f"Gold | Transform failed | {e}")
        raise

    finally:
        if silver_con: close_db(silver_con)
        if gold_con:   close_db(gold_con)
        if ops_con:    close_db(ops_con)


if __name__ == "__main__":
    transform_silver_to_gold()