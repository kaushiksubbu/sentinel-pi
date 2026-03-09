# ingest_data.py
import os
import logging
import subprocess
import sys
import time
from load_knmi_to_bronze import load_knmi_files_to_bronze
from datetime import datetime
from dotenv import load_dotenv

from transform_knmi_to_silver import transform_knmi_to_silver
from transform_zigbee_to_silver import transform_zigbee_to_silver
from transform_silver_to_gold import transform_silver_to_gold

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

# KNMI modules
from knmi_utils import fetch_knmi_file
from weather_utils import extract_station_data
from load_KNMI_to_duckdb import save_weather_to_duckdb

# Zigbee loading module
from load_zigbee_to_duckdb import load_zigbee_to_duckdb

load_dotenv("/mnt/data/sentinel-pi/.env")

# --- Paths ---
BRONZE_LANDING = "/mnt/data/sentinel-pi/data/bronze/landing_zone"
BRONZE_DB     = "/mnt/data/sentinel-pi/data/bronze/raw_source.db"
SILVER_DB     = "/mnt/data/sentinel-pi/data/silver/master_data.db"
PROJECT_DIR   = "/mnt/data/sentinel-pi"
VENV_PYTHON   = "/mnt/data/sentinel-pi/.venv/bin/python3"
COLLECT_ZIGBEE_SCRIPT = "/mnt/data/sentinel-pi/src/collect_zigbee_data.py"

# --- Constants ---
BRONZE_ZIGBEE_TBL = "zigbee_raw"
BRONZE_KNMI_TBL   = "knmi_raw"
SILVER_WEATHER_TBL   = "weather_silver"

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
            base_url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/10-minute-in-situ-meteorological-observations/versions/1.0/files",
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
    logging.info("Loading Zigbee data from Bronze JSONs → Bronze DuckDB table...")
    load_zigbee_to_duckdb(
        db_path=BRONZE_DB,  
        table=BRONZE_ZIGBEE_TBL,
        landing_dir=BRONZE_LANDING,
    )

# --- Main entrypoint (master ingest) ---
def main():
    # Ensure Bronze landing exists
    os.makedirs(BRONZE_LANDING, exist_ok=True)

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


if __name__ == "__main__":
    main()