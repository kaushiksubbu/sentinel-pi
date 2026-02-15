import duckdb

# Config - Using the separate Sentinel DB for master data
DB_PATH = 'data/sentinel_pi.db'
CSV_PATH = '/mnt/data/sentinel-pi/data/csv_knmi_nl_20251017.csv'

def load_master_stations():
    con = duckdb.connect(DB_PATH)
    
    print(f"Loading full Master Data from {CSV_PATH}...")

    try:
        # 1. Create the Master Table (Silver Layer)
        # We include WSI and RD coordinates (POS_X/Y) for future GIS work
        con.execute("""
            CREATE TABLE IF NOT EXISTS main.master_stations (
                station_code VARCHAR PRIMARY KEY,
                wigos_id VARCHAR,
                operational_start DATE,
                operational_stop DATE,
                location_name VARCHAR,
                station_type VARCHAR,
                elevation_m DOUBLE,
                rd_x DOUBLE,
                rd_y DOUBLE,
                latitude DOUBLE,
                longitude DOUBLE
            );
        """)

        # 2. Bulk Load using COPY (High Performance)
        # We use a temp view to handle the data cleaning (dates) before inserting
        con.execute(f"""
            INSERT OR REPLACE INTO main.master_stations
            SELECT 
                CAST(STN AS VARCHAR) as station_code,
                WSI as wigos_id,
                -- Handle KNMI date format (YYYYMMDD) or NULL
                TRY_CAST(strptime(CAST(STARTT AS VARCHAR), '%Y-%m-%d') AS DATE) as operational_start,
                -- Handle stop date (often 99991231 for active)
                CASE 
                    WHEN CAST(STOPT AS VARCHAR) IN ('99991231', '9999-12-31') THEN NULL 
                    ELSE TRY_CAST(strptime(CAST(STOPT AS VARCHAR), '%Y-%m-%d') AS DATE)
                END as operational_stop,
                LOCATIE as location_name,
                TYPE as station_type,
                HOOGTE as elevation_m,
                POS_X as rd_x,
                POS_Y as rd_y,
                POS_NB as latitude,
                POS_OL as longitude
            FROM read_csv('{CSV_PATH}', header=True, auto_detect=True);
        """)
        
        total_rows = con.execute("SELECT COUNT(*) FROM main.master_stations").fetchone()[0]
        print(f"✅ Master Station Data Loaded: {total_rows} stations available.")

    except Exception as e:
        print(f"Master Load failed: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    load_master_stations()