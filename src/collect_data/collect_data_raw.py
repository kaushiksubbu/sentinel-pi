# collect_data_raw.py

import os
import sys
import logging
from dotenv import load_dotenv

from collect_data_knmi import collect_knmi
from collect_data_zigbee import collect_zigbee

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common_func'))

from config import (
    BRONZE_LANDING,
)

LOG_FILE = "/mnt/data/sentinel-pi/logs/cron.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename=LOG_FILE,
    filemode="a",
    force=True,
)

load_dotenv("/mnt/data/sentinel-pi/.env")


def main():
    # Ensure Bronze landing exists
    os.makedirs(BRONZE_LANDING, exist_ok=True)

    # 1. Collect KNMI → Bronze
    knmi_file = collect_knmi()
    if not knmi_file:
        logging.warning("No KNMI file collected; skipping KNMI load.")
        return

    # 2. Collect Zigbee → landing zone
    collect_zigbee()


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        logging.warning("Fetch process did not complete")
