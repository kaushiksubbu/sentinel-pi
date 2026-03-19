from prefect import flow, task
import subprocess
import logging
import sys 
from prefect.server.schemas.schedules import IntervalSchedule
from datetime import timedelta

from dotenv import load_dotenv
import os

load_dotenv("/mnt/data/sentinel-pi/.env")

VENV_PYTHON = "/mnt/data/sentinel-pi/.venv/bin/python3"

@task(name="sentinel-pipeline-run", retries=2, retry_delay_seconds=30)
def run_pipeline():
    result = subprocess.run(
        [VENV_PYTHON, "/mnt/data/sentinel-pi/src/ingest_data.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Pipeline failed: {result.stderr}")
    return result.stdout

@flow(name="sentinel-pipeline")
def sentinel_pipeline():
    from datetime import timedelta
    run_pipeline()

if __name__ == "__main__":
    sentinel_pipeline.serve(
        name="sentinel-pi-schedule",
        interval=timedelta(minutes=10)
    )