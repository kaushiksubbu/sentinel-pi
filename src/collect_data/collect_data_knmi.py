import os
import logging
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common_func'))


# KNMI modules
from knmi_utils import fetch_knmi_file

from config import (
    BRONZE_LANDING,
    KNMI_BASE_URL
)


def collect_knmi():
    logging.info("Starting KNMI data collection (Bronze)...")
    try:
        file_path = fetch_knmi_file(
            api_key=os.getenv("KNMI_API_KEY"),
            base_url=KNMI_BASE_URL,
            destination_dir=BRONZE_LANDING,
        )
        logging.info(f"KNMI raw file saved to: {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"KNMI collection failed: {str(e)}")
        raise


if __name__ == "__main__":
    # 1. Collect KNMI Raw files.
    knmi_file = collect_knmi()
