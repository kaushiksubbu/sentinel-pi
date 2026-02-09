import duckdb
import os
import json
from datetime import datetime

# --- CONFIGURATION  ---
# Get the directory where the script lives to make it portable #
PROJECT_ROOT = "/mnt/data/sentinel-pi"
LANDING_DIR   = os.path.join(PROJECT_ROOT, "data/landing_zone")
# Note: point the DB to the 'warehouse' folder created
DB_PATH      = os.path.join(PROJECT_ROOT, "data/warehouse/sentinel.db")

# Ensure Root directory exist
os.makedirs(PROJECT_ROOT, exist_ok=True)
# Ensure these directories exist before writing
os.makedirs(os.path.dirname(LANDING_DIR), exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# --- FUNCTION 1: FETCH & LAND (The 'Bronze' Act) ---
def fetch_and_land_weather():
    """Fetches raw data and saves it as an immutable JSON file."""
    print("🛰️ Step 1: Fetching Raw Weather...")
    
    # Placeholder for the KNMI API response
    raw_payload = {
        "station": "Schiphol",
        "temp_c": 10.5,
        "humidity":78,
        "wind_knts": 14,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save to Bronze as a 'Point in Time' file
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M')
    file_path = f"{LANDING_DIR}/weather_{timestamp_str}.json"
    
    with open(file_path, 'w') as f:
        json.dump(raw_payload, f)
    
    print(f"✅ Bronze: Data landed at {file_path}")
    return raw_payload

# --- FUNCTION 2: PROCESS & PROMOTE (The 'Silver' Act) ---
def promote_to_silver(data):
    """Takes raw data and inserts it into the Iceberg table."""
    print("💎 Step 2: Promoting to Silver (Iceberg)...")
    
    con = duckdb.connect(DB_PATH)
    con.execute("INSTALL iceberg; LOAD iceberg;")
    
    # Create the Table with Iceberg format
    con.execute("""
        CREATE TABLE IF NOT EXISTS weather_silver (
            station VARCHAR,
            temp_c DOUBLE,
            humidity INTEGER,
            wind_knts INTEGER,
            ts TIMESTAMP
        )
    """)
    
    # Insert data
    con.execute(f"""
        INSERT INTO weather_silver 
        VALUES ('{data['station']}', {data['temp_c']}, {data['humidity']}, {data['wind_knts']}, '{data['timestamp']}')
    """)
    con.close()
    print("🏆 Success: Database updated.")

# --- MAIN EXECUTION (The 'Orchestration' Layer) ---
if __name__ == "__main__":
    # This flow is what a TPM manages: Fetch -> Land -> Process
    raw_data = fetch_and_land_weather()
    promote_to_silver(raw_data)