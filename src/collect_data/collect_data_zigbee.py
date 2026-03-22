# --- Collect Zigbee → Bronze (JSON files) ---
from config import (
    PROJECT_DIR,
    COLLECT_ZIGBEE_SCRIPT,  # ← ADD THIS
)
from datetime import datetime, timezone
from pipeline_logger import write_jsonl_entry
import os
import logging
import subprocess
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))


def collect_zigbee():
    start_time = datetime.now(timezone.utc)
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
            write_jsonl_entry(
                stage="collect_zigbee_wrapper",
                status="error",
                start_time=start_time,
                error=result.stderr
            )
    except Exception as e:
        logging.error(f"Error running Zigbee collection: {str(e)}")
        write_jsonl_entry(
            stage="collect_zigbee_wrapper",
            status="error",
            start_time=start_time,
            error=str(e)
        )
        raise


if __name__ == "__main__":
    # 1. Collect Zigbee Raw files.
    collect_zigbee()
