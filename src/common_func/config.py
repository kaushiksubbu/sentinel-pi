# config.py
BRONZE_DB    = '/mnt/data/sentinel-pi/data/bronze/raw_source.db'
SILVER_DB    = '/mnt/data/sentinel-pi/data/silver/master_data.db'
GOLD_DB      = '/mnt/data/sentinel-pi/data/gold/analytics.db'
REFERENCE_DB = '/mnt/data/sentinel-pi/data/reference/reference.db'
OPS_DB = '/mnt/data/sentinel-pi/data/ops/ops.db'

# thresholds limits
KNMI_COMPLETENESS_MIN    = 0.84
ZIGBEE_COMPLETENESS_MIN  = 0.94

# db_utils.py functions:
# connect_to_db()          → write connections (pipeline only)
# connect_to_db_readonly() → read connections (AI, queries, reporting)
# close_db()               → always close after use

#lock files
LOCK_FILE  = "/mnt/data/sentinel-pi/locks/etl.lock"
LOCK_META  = "/mnt/data/sentinel-pi/locks/etl_lock_meta.json"

# --- Paths ---
PROJECT_DIR   = "/mnt/data/sentinel-pi"
VENV_PYTHON   = "/mnt/data/sentinel-pi/.venv/bin/python3"
COLLECT_ZIGBEE_SCRIPT = "/mnt/data/sentinel-pi/src/collect_data/collect_zigbee_files.py"
BRONZE_LANDING    = "/mnt/data/sentinel-pi/data/bronze/landing_zone"
PROCESSED_DIR  = "/mnt/data/sentinel-pi/data/bronze/landing_zone/processed"
REPORTS_DIR = "/mnt/data/sentinel-pi/docs/daily_reports"

# Project paths
PROJECT_DIR           = "/mnt/data/sentinel-pi"
VENV_PYTHON           = "/mnt/data/sentinel-pi/.venv/bin/python3"

# Table names
BRONZE_ZIGBEE_TBL  = "zigbee_raw"
BRONZE_KNMI_TBL    = "knmi_raw"
SILVER_WEATHER_TBL = "weather_silver"

# --- Constants ---
STATIONS = ['06269', '06240']  # Lelystad, Schiphol

# External APIs
KNMI_BASE_URL = (
    "https://api.dataplatform.knmi.nl/open-data/v1/datasets"
    "/10-minute-in-situ-meteorological-observations"
    "/versions/1.0/files"
)

# Log file area
LOG_FILE            = "/mnt/data/sentinel-pi/logs/cron.log"
STRUCTURED_LOG_FILE = "/mnt/data/sentinel-pi/logs/pipeline.jsonl"

# Ollama Config
import os
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)
OLLAMA_MODEL = "llama3.2:1b-instruct-q4_K_M"
