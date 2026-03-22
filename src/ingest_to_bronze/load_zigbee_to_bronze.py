# load_zigbee_to_bronze.py

from datetime import datetime, timezone
from metrics_contract import BronzeMetrics
from pipeline_logger import write_jsonl_entry
from db_utils import (
    connect_to_db,
    close_db,
    create_table_with_ddl,
    bulk_insert_ignore,
)
from config import BRONZE_DB, BRONZE_ZIGBEE_TBL, BRONZE_LANDING
import os
import json
import glob
import db_utils
import logging
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))


def read_zigbee_jsons(landing_dir: str) -> list:
    """
    Read all zigbee JSON files and normalize to rows.
    Returns list of dicts (topic, payload, timestamp, source_file).
    """
    records = []
    pattern = os.path.join(landing_dir, "zigbee_*.json")

    for path in glob.glob(pattern):
        try:
            with open(path, "r") as f:
                data = json.load(f)

            if "messages" in data:
                # 5‑minute window holding list of messages
                for msg in data["messages"]:
                    records.append({
                        "topic": msg["topic"],
                        "payload": msg["payload"],
                        "timestamp": msg["timestamp"],
                        "source_file": path,
                    })
            else:
                # Single snapshot style
                records.append({
                    "topic": data["topic"],
                    "payload": data["payload"],
                    "timestamp": data["timestamp"],
                    "source_file": path,
                })
        except Exception as e:
            logging.error(f"Error reading {path}: {e}")

    return records


def load_zigbee_to_duckdb(db_path: str, table: str, landing_dir: str):
    """
    Load all Zigbee JSONs into a DuckDB table (Bronze) via db_utils.
    """
    logging.info("=== ZIGBEE_LOAD_START ===")
    start_time = datetime.now(timezone.utc)

    try:
        con = db_utils.connect_to_db(db_path)
        con.execute("SELECT 1")  # Test connection
        con.close()
        logging.info("DB connection OK")

    except Exception as db_err:
        logging.error(f"DB connection FAILED: {db_err}")
        logging.error("=== ZIGBEE_LOAD_FAILED ===")
        return

    try:
        # Find Zigbee files
        zigbee_files = glob.glob(os.path.join(landing_dir, "zigbee_*.json"))
        if not zigbee_files:
            logging.warning("No Zigbee files found in landing zone")
            logging.info("=== ZIGBEE_LOAD_SKIP (no files) ===")
            return

        logging.info(f"Found {len(zigbee_files)} Zigbee files")

        # Read and load data
        rows = []
        for file_path in zigbee_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Handle your nested structure: {"topic": "...", "messages": [...]}
                if isinstance(data, dict) and "messages" in data:
                    file_topic = data.get("topic", "unknown")
                    messages = data.get("messages", [])

                    for message in messages:
                        if isinstance(message, dict):
                            rows.append({
                                # Prefer message topic
                                "topic": message.get("topic", file_topic),
                                "payload": json.dumps(message.get("payload", {})),
                                "timestamp": datetime.fromisoformat(message.get("timestamp", "2026-01-01T00:00:00")),
                                "source_file": os.path.basename(file_path)
                            })
                else:
                    logging.warning(
                        f"Unexpected format in {file_path}: {type(data)}")

            except Exception as e:
                logging.error(f"Failed to parse {file_path}: {e}")

        if not rows:
            logging.warning("No valid Zigbee data to load")
            logging.info("=== ZIGBEE_LOAD_SKIP (no data) ===")
            return

        # Load to DuckDB
        con = db_utils.connect_to_db(db_path)

        # Infer schema from first row
        sample_row = rows[0]
        inferred_schema = db_utils.infer_schema(sample_row)
        logging.info(f"Inferred schema for Zigbee: {inferred_schema}")

        db_utils.create_table_if_not_exists(con, table, inferred_schema)
        db_utils.upsert_or_append(con, table, rows)

        logging.info(f"Loaded {len(rows)} Zigbee records")

        # Move processed files
        processed_dir = os.path.join(landing_dir, "processed")
        os.makedirs(processed_dir, exist_ok=True)

        for file_path in zigbee_files:
            try:
                dest_path = os.path.join(
                    processed_dir, os.path.basename(file_path))
                os.rename(file_path, dest_path)
                logging.info(
                    f"Moved: {os.path.basename(file_path)} → processed/")
            except Exception as move_err:
                logging.error(f"Failed to move {file_path}: {move_err}")

        logging.info("=== ZIGBEE_LOAD_SUCCESS ===")
        write_jsonl_entry(
            stage="load_zigbee_bronze",
            status="success",
            start_time=start_time,
            metrics=BronzeMetrics(records_landed=len(rows))
        )

    except Exception as e:
        logging.error(f"ZIGBEE_LOAD_FAILED: {str(e)}")
        logging.error(f"  Type: {type(e).__name__}")
        import traceback
        logging.error(f"  Traceback: {traceback.format_exc()}")
        logging.info("=== ZIGBEE_LOAD_FAILED ===")
        write_jsonl_entry(
            stage="load_zigbee_bronze",
            status="error",
            start_time=start_time,
            error=str(e)
        )
    finally:
        close_db(con)


if __name__ == "__main__":
    logging.info(
        "Loading Zigbee data from Bronze JSONs → Bronze DuckDB table...")
    load_zigbee_to_duckdb(
        db_path=BRONZE_DB,
        table=BRONZE_ZIGBEE_TBL,
        landing_dir=BRONZE_LANDING,
    )
