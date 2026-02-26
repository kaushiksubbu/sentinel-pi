import duckdb
import os

# Define Silo Paths
BRONZE_DB = 'data/bronze/raw_source.db'
SILVER_DB = 'data/silver/master_data.db'
GOLD_DB   = 'data/gold/analytics.db'

def build_medallion():
    print("Starting Medallion Rebuild...")

    # --- 1. BRONZE: RAW INGESTION ---
    # We take the CSV exactly as it is.
    # 1. Open Connection
    con = duckdb.connect(BRONZE_DB)
    
    print("🛠️  Ingesting CSV to Bronze...")
    # We use 'sep=auto' and skip the header issue by naming columns manually
    con.execute("""
        CREATE OR REPLACE TABLE knmi_raw AS 
        SELECT * FROM read_csv('data/bronze/knmi_stations.csv', 
            header=True, 
            auto_detect=True);
    """)

    # Check if data actually landed
    count = con.execute("SELECT count(*) FROM knmi_raw").fetchone()[0]
    print(f"Bronze Count: {count} rows")

    # --- 2. SILVER: DATA QUALITY & CLEANSING ---
    print("Step 2: Refining to Silver (Cleansing)...")
    s_con = duckdb.connect(SILVER_DB)
    s_con.execute(f"ATTACH '{BRONZE_DB}' AS bronze_db;")
    
    # Using double quotes around column names to handle the "Binder Error"
    s_con.execute("""
        CREATE OR REPLACE TABLE stations_cleansed AS
        SELECT 
            STN AS station_id,
            TRIM(LOCATIE) AS location,
            POS_NB AS lat,
            POS_OL AS lon,
            HOOGTE AS elevation_m
        FROM bronze_db.knmi_raw
        WHERE 
            STN IS NOT NULL                 -- Quality Check 1: ID exists
            AND POS_NB BETWEEN 50.0 AND 55.0 -- Quality Check 2: Valid Lat
            AND POS_OL BETWEEN 3.0 AND 8.0;  -- Quality Check 3: Valid Lon
    """)
    s_con.close()

    # --- 3. GOLD: ANALYTICS & AI READINESS ---
    # We create a specific view for your Almere/Flevoland context.
    print("Step 3: Promoting to Gold (Almere View)...")
    g_con = duckdb.connect(GOLD_DB)
    g_con.execute(f"ATTACH '{SILVER_DB}' AS silver_db;")
    g_con.execute("""
        CREATE OR REPLACE VIEW almere_context AS
        SELECT * FROM silver_db.stations_cleansed
        WHERE location ILIKE '%Almere%' 
           OR location ilike 'Lelystad%' 
           or location ilike 'Schiphol%';
    """)
    g_con.close()

    print("\n Medallion Pipeline Complete.")
    print(f"Location: {os.getcwd()}")

if __name__ == "__main__":
    build_medallion()