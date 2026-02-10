import os
from dotenv import load_dotenv

# Import your custom modular toolkit
from knmi_utils import fetch_knmi_file
from weather_utils import extract_station_data
from db_utils import save_weather_to_duckdb

load_dotenv("/mnt/data/sentinel-pi/.env")

# Project Settings
DB_PATH = "/mnt/data/sentinel-pi/data/weather_lake.db"
LANDING_DIR = "/mnt/data/sentinel-pi/data/landing_zone"
API_KEY = os.getenv("KNMI_API_KEY")
KNMI_URL = "https://api.dataplatform.knmi.nl/open-data/v1/datasets/10-minute-in-situ-meteorological-observations/versions/1.0/files"

# Define which station to take - for now defining Lelystad
STATION_ID = '06269'
TARGET_TABLE = "weather_observations"

def main():
    print("Running Modular Pipeline...")
    try:
        # 1. Fetch
        file_path = fetch_knmi_file(API_KEY, KNMI_URL, LANDING_DIR)
        
        # 2. Extract

        weather = extract_station_data(file_path,STATION_ID)
        
        # 3. Save
        save_weather_to_duckdb(DB_PATH, TARGET_TABLE, weather, STATION_ID)
        
        print(f"Job Finished. Recorded: {weather['temp']}°C at {weather['timestamp']}")
        
    except Exception as e:
        print(f"Pipeline error: {e}")

if __name__ == "__main__":
    main()