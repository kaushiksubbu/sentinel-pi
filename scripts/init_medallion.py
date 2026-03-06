# MANUAL RUN ONLY — never add to cron
# Purpose: One-time reference data load from KNMI stations CSV
# Frequency: Run only when KNMI station data changes
# Last run: [26-02-2026]

import os
from db_utils import connect_to_db, close_db, create_table_with_ddl
import logging
from config import BRONZE_DB, REFERENCE_DB

def load_KNMI_stations():
    logging.info("Starting KNMI Station load...")

    # --- 1. BRONZE: RAW INGESTION ---
    # We take the CSV exactly as it is.
    con = None
    try:
        # 1. Open Connection
        con = connect_to_db(BRONZE_DB)
        logging.info("🛠️  Ingesting CSV to Bronze...")
        # We use 'sep=auto' and skip the header issue by naming columns manually
        con.execute("""
            CREATE OR REPLACE TABLE knmi_raw AS 
            SELECT * FROM read_csv('data/bronze/knmi_stations.csv', 
                header=True, 
                auto_detect=True);
        """)
            # Check if data actually landed
        count = con.execute("SELECT count(*) FROM knmi_raw").fetchone()[0]
        logging.info(f"Bronze Count: {count} rows")
    finally:
        if con:        
            close_db(con)

    # --- 2. Reference : DATA QUALITY & CLEANSING ---
    logging.info("Step 2: Refining to Reference (Cleansing)...")
    ref_con = None
    try:
        ref_con = connect_to_db(REFERENCE_DB)
        ref_con.execute(f"ATTACH '{BRONZE_DB}' AS bronze_db;")

        # Using double quotes around column names to handle the "Binder Error"
        ref_con.execute("""
            CREATE OR REPLACE TABLE stations AS
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
    finally:
            if ref_con:        
                close_db(ref_con)

    logging.info("\n One time KNMI Station load Pipeline Complete.")
    logging.info(f"Location: {os.getcwd()}")

if __name__ == "__main__":
    load_KNMI_stations()