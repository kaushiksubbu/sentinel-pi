from prefect import flow, task
import subprocess
import logging
import sys 
from prefect.server.schemas.schedules import IntervalSchedule
from datetime import timedelta

VENV_PYTHON = "/mnt/data/sentinel-pi/.venv/bin/python3"

@task(name="land-bronze", retries=2, retry_delay_seconds=30)
def land_bronze():
    logging.info("Starting land-bronze...")
    result = subprocess.run(
        [VENV_PYTHON, "/mnt/data/sentinel-pi/src/load_knmi_to_bronze.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"land-bronze failed: {result.stderr}")
    logging.info("land-bronze complete")
    return result.stdout

@task(name="transform-silver", retries=2, retry_delay_seconds=30)
def transform_silver():
    logging.info("Starting transform-silver...")
    result = subprocess.run(
        [VENV_PYTHON, "/mnt/data/sentinel-pi/src/transform_knmi_to_silver.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"transform-silver failed: {result.stderr}")
    logging.info("transform-silver complete")
    return result.stdout

@task(name="transform-gold", retries=2, retry_delay_seconds=30)
def transform_gold():
    logging.info("Starting transform-gold...")
    result = subprocess.run(
        [VENV_PYTHON, "/mnt/data/sentinel-pi/src/transform_silver_to_gold.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"transform-gold failed: {result.stderr}")
    logging.info("transform-gold complete")
    return result.stdout

@task(name="ai-summary", retries=1, retry_delay_seconds=60)
def ai_summary():
    logging.info("Starting ai-summary...")
    result = subprocess.run(
        [VENV_PYTHON, "/mnt/data/sentinel-pi/src/ai_summary.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"ai-summary failed: {result.stderr}")
    logging.info("ai-summary complete")
    return result.stdout

@flow(name="sentinel-pipeline")
def sentinel_pipeline():
    bronze = land_bronze()
    silver = transform_silver(wait_for=[bronze])
    gold = transform_gold(wait_for=[silver])
    ai_summary(wait_for=[gold])

if __name__ == "__main__":
    sentinel_pipeline.serve(
        name="sentinel-pi-schedule",
        interval=timedelta(minutes=10)
    )