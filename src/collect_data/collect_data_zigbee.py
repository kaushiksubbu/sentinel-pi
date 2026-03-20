# --- Collect Zigbee → Bronze (JSON files) ---
import os
import logging
import subprocess
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common_func'))


from config import (
    PROJECT_DIR,
    COLLECT_ZIGBEE_SCRIPT,
)

LOG_FILE = "/mnt/data/sentinel-pi/logs/cron.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def collect_zigbee():
    logging.info("Starting Zigbee data collection (Bronze)...")
    try:
        result = subprocess.run(
            [sys.executable, COLLECT_ZIGBEE_SCRIPT],
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


if __name__ == "__main__":
    # 1. Collect Zigbee Raw files.
    collect_zigbee()
