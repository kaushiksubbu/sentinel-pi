# load_zigbee_to_duckdb.py
import os
import json
import glob
from datetime import datetime
import db_utils
import logging

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

    con = db_utils.connect_to_db(db_path)

    # 1. Schema for Zigbee Bronze table
    schema = {
        "topic": "VARCHAR",
        "payload": "JSON",
        "timestamp": "TIMESTAMP",
        "source_file": "VARCHAR",
    }

    db_utils.create_table_if_not_exists(con, table, schema)

    # 2. Read data
    rows = read_zigbee_jsons(landing_dir)
    if not rows:
        logging.warning(f"No Zigbee data to load. No JSON files found in {landing_dir} or they were empty.")
        db_utils.close_db(con)
        return

    logging.info(f"Loaded {len(rows)} Zigbee records.")

    # 3. Convert to tuples
    values = [
        (row["topic"], row["payload"], row["timestamp"], row["source_file"])
        for row in rows
    ]

    # 4. Append to DuckDB Bronze table
    db_utils.upsert_or_append(
        con=con,
        table=table,
        rows=values,
        on_conflict=None,
    )

    db_utils.close_db(con)
    logging.info(f"Zigbee data written to {db_path}::{table}")
    logging.info("=== ZIGBEE_LOAD_STOP ===")