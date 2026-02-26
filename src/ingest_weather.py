import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from knmi_utils import fetch_knmi_file
from weather_utils import extract_station_data
from db_utils import save_weather_to_duckdb

load_dotenv("/mnt/data/sentinel-pi/.env")

# --- Updated Medallion Paths ---
BRONZE_LANDING = "/mnt/data/sentinel-pi/data/bronze/landing_zone"
SILVER_DB = "/mnt/data/sentinel-pi/data/silver/master_data.db"
LOG_FILE = "/mnt/data/sentinel-pi/logs/cron.log"

API_KEY = os.getenv("KNMI_API_KEY")
KNMI_URL = "https://api.dataplatform.knmi.nl/open-data/v1/datasets/10-minute-in-situ-meteorological-observations/versions/1.0/files"
STATIONS = ['06269', # Lelystad
            '06240' # Schiphol Airport
            ]

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def validate_data(data,station_id):
    """Week 2: Data Quality Logic"""
    if data['temp'] is None:
        return False, f"STATION_{station_id}_NULL_VALUE"
    
    if not (-25 < data['temp'] < 45): # Realistic NL range
        return False, f"STATION_{station_id}_OUT_OF_RANGE: {temp}C"
    return True, "OK"

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # 1. BRONZE: Fetch and keep the raw file
        # We keep LANDING_DIR as part of our Bronze 'history'
        file_path = fetch_knmi_file(API_KEY, KNMI_URL, BRONZE_LANDING)
        
        # 2. SILVER EXTRACTION
        for s_id in STATIONS:
            try:
                # Extract specific station data
                weather = extract_station_data(file_path, s_id)
                
                # 3. QUALITY GATE
                is_valid, reason = validate_data(weather, s_id)
                
                if is_valid:
                    # 4. SILVER: Save to master database
                    save_weather_to_duckdb(SILVER_DB, "weather_observations", weather, s_id)
                    logging.info(f"DATA_SUCCESS | Station: {s_id} | Weather: {weather}")
                    #log_msg = f"[{timestamp}] DATA_SUCCESS | Station: {s_id} | Weather: {weather}C\n"
                else:
                    logging.warning(f"DATA_QUALITY_ALERT | | Station: {s_id} | Reason: {reason} | Weather: {weather}")
                    #log_msg = f"[{timestamp}] QUALITY_ALERT | Station: {s_id} | Reason: {reason}\n"                
                
                # Append to Cron Log
                #with open(LOG_FILE, "a") as f:
                #    logging.info(log_msg)
                    
            except Exception as station_err:
                with open(LOG_FILE, "a") as f:
                    f.write(f"[{timestamp}] ERROR | Station: {s_id} | {str(station_err)}\n")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] CRITICAL_SYSTEM_ERROR | {str(e)}\n")
        print(f"Pipeline crashed: {e}")

if __name__ == "__main__":
    # Ensure the directory exists before fetching
    os.makedirs(BRONZE_LANDING, exist_ok=True)
    main()