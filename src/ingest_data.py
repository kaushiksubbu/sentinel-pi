# ingest_data.py

from filelock import FileLock, Timeout
import os
import json
import logging
import subprocess

from load_knmi_to_bronze import load_knmi_files_to_bronze
from datetime import datetime, timezone
from dotenv import load_dotenv

from transform_knmi_to_silver import transform_knmi_to_silver
from transform_zigbee_to_silver import transform_zigbee_to_silver
from transform_silver_to_gold import transform_silver_to_gold

# KNMI modules
from knmi_utils import fetch_knmi_file

# Zigbee loading module
from load_zigbee_to_duckdb import load_zigbee_to_duckdb

from config import (
    BRONZE_DB,
    LOCK_FILE,
    LOCK_META,
    BRONZE_LANDING,
    PROJECT_DIR,
    VENV_PYTHON,
    BRONZE_ZIGBEE_TBL,
    COLLECT_ZIGBEE_SCRIPT,
    KNMI_BASE_URL
)

LOG_FILE = "/mnt/data/sentinel-pi/logs/cron.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename=LOG_FILE,
    filemode="a",
    force=True,
)


load_dotenv("/mnt/data/sentinel-pi/.env")


def validate_data(data, station_id):
    """Data quality gate for KNMI."""
    temp = data.get("temp")
    if temp is None:
        return False, f"STATION_{station_id}_NULL_VALUE"
    if not (-25 < temp < 45):  # realistic NL range
        return False, f"STATION_{station_id}_OUT_OF_RANGE: {temp}C"
    return True, "OK"

# --- 1. Collect KNMI → Bronze (raw file) ---


def collect_knmi():
    logging.info("Starting KNMI data collection (Bronze)...")
    try:
        file_path = fetch_knmi_file(
            api_key=os.getenv("KNMI_API_KEY"),
            base_url=KNMI_BASE_URL,
            destination_dir=BRONZE_LANDING,
        )
        logging.info(f"KNMI raw file saved to: {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"KNMI collection failed: {str(e)}")
        raise

# --- 3. Collect Zigbee → Bronze (JSON files) ---


def collect_zigbee():
    logging.info("Starting Zigbee data collection (Bronze)...")
    try:
        result = subprocess.run(
            [VENV_PYTHON, COLLECT_ZIGBEE_SCRIPT],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logging.info("Zigbee data collection completed (Bronze).")
        else:
            logging.error(f"Zigbee collection failed: {result.stderr}")
    except Exception as e:
        logging.error(f"Error running Zigbee collection: {str(e)}")


# --- 4. Load Zigbee (Bronze JSONs → DuckDB Bronze table) ---
def load_zigbee():
    logging.info(
        "Loading Zigbee data from Bronze JSONs → Bronze DuckDB table...")
    load_zigbee_to_duckdb(
        db_path=BRONZE_DB,
        table=BRONZE_ZIGBEE_TBL,
        landing_dir=BRONZE_LANDING,
    )


def write_lock_meta():
    """Write lock identifier for observability and log parsing."""
    meta = {
        "pid": os.getpid(),
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "script": "ingest_data.py"
    }
    with open(LOCK_META, 'w') as f:
        json.dump(meta, f)
    logging.info(
        f"Lock acquired | PID: {meta['pid']} | "
        f"Time: {meta['acquired_at']}"
    )


def clear_lock_meta():
    """Remove lock metadata on release."""
    if os.path.exists(LOCK_META):
        os.remove(LOCK_META)
    logging.info(f"Lock released | PID: {os.getpid()}")

# --- Main entrypoint (master ingest) ---


def main():
    # Ensure Bronze landing exists
    os.makedirs(BRONZE_LANDING, exist_ok=True)

    # start of cycle
    logging.info("Start of load cycle")

    # 1. Collect KNMI → Bronze
    knmi_file = collect_knmi()
    if not knmi_file:
        logging.warning("No KNMI file collected; skipping KNMI load.")
        return

    # 2. Load KNMI landing zone → Bronze DuckDB
    load_knmi_files_to_bronze()

    # 3. Transform KNMI Bronze → Silver
    transform_knmi_to_silver()

    # 4. Collect Zigbee → landing zone
    collect_zigbee()

    # 5. Load Zigbee → Bronze DuckDB
    load_zigbee()

    # 6. Transform Zigbee Bronze → Silver  ← ADD
    transform_zigbee_to_silver()

    # 7. Transform Silver → Gold
    transform_silver_to_gold()

    # Log to close the run
    logging.info("End of load cycle")


if __name__ == "__main__":
    try:
        with FileLock(LOCK_FILE, timeout=0):
            write_lock_meta()
            main()
            clear_lock_meta()
    except Timeout:
        logging.warning(
            f"Pipeline already running — skipping this run. "
            f"Check {LOCK_META} for lock owner."
        )
