# purge_processed_files.py
# Deletes raw files older than 10 days from processed folder.
# MANUAL or CRON — never a Prefect task.
# Cron suggestion: 0 2 * * * (daily 02:00)

import os
import time
import logging

PROCESSED_DIR = "/mnt/data/sentinel-pi/data/bronze/landing_zone/processed"
MAX_AGE_DAYS = 10
MAX_AGE_SECONDS = MAX_AGE_DAYS * 86400

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def purge_old_files(processed_dir: str, max_age_seconds: int):
    now = time.time()
    deleted = 0
    skipped = 0

    for filename in os.listdir(processed_dir):
        filepath = os.path.join(processed_dir, filename)
        if not os.path.isfile(filepath):
            continue
        file_age = now - os.path.getmtime(filepath)
        if file_age > max_age_seconds:
            os.remove(filepath)
            logging.info(f"Deleted: {filename} (age: {int(file_age // 86400)} days)")
            deleted += 1
        else:
            skipped += 1

    logging.info(f"Purge complete | Deleted: {deleted} | Skipped: {skipped}")


if __name__ == "__main__":
    purge_old_files(PROCESSED_DIR, MAX_AGE_SECONDS)