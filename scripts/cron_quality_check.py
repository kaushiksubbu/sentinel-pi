import duckdb
from datetime import datetime
import os

# Paths (Using absolute paths for Cron reliability)
BASE_DIR = "/mnt/data/sentinel-pi"
GOLD_DB = f"{BASE_DIR}/data/gold/analytics.db"
SILVER_DB = f"{BASE_DIR}/data/silver/master_data.db"
LOG_FILE = f"{BASE_DIR}/logs/cron.log"

def run_checks():
    con = duckdb.connect(GOLD_DB)
    # Re-attach the link that was missing earlier
    con.execute(f"ATTACH '{SILVER_DB}' AS silver_db;")
    
    # 1. Null Value Check
    nulls = con.execute("SELECT count(*) FROM almere_context WHERE lat IS NULL OR lon IS NULL").fetchone()[0]
    
    # 2. Out-of-Range Check (Using NL bounds as the quality gate)
    # If a station is suddenly at Lat 0, we need a flag.
    out_of_bounds = con.execute("SELECT count(*) FROM almere_context WHERE lat < 50 OR lat > 54").fetchone()[0]

    # 3. Format the log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] QUALITY_CHECK: Nulls={null_count} | OutOfRange={out_of_bounds} | "
        f"Status={'FAIL' if nulls > 0 or out_of_bounds > 0 else 'PASS'}\n"
    )

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    
    con.close()

if __name__ == "__main__":
    run_checks()