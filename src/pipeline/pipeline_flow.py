import sys
import subprocess
from datetime import timedelta
from dotenv import load_dotenv
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

load_dotenv("/mnt/data/sentinel-pi/.env")

VENV_PYTHON = sys.executable


def docker_run(image: str, extra_flags: list = []):
    cmd = [
        "docker", "run", "--rm",
        "-v", "/mnt/data/sentinel-pi/src:/mnt/data/sentinel-pi/src",
        "-v", "/mnt/data/sentinel-pi/data:/mnt/data/sentinel-pi/data",
        "-v", "/mnt/data/sentinel-pi/logs:/mnt/data/sentinel-pi/logs",
        "-e", "TZ=Europe/Amsterdam",
        "-e", f"PREFECT_RUN_NAME={flow_run.name}",  
        "--env-file", "/mnt/data/sentinel-pi/.env",
    ] + extra_flags + [image]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"{image} failed:\n{result.stderr}")
    return result.stdout


@task(name="collect-knmi", retries=2, retry_delay_seconds=30)
def collect_knmi():
    return docker_run("sentinel-pi-collect-knmi:v1.0")


@task(name="collect-zigbee", retries=2, retry_delay_seconds=30)
def collect_zigbee():
    return docker_run("sentinel-pi-collect-zigbee:v1.0")


@task(name="load-knmi-bronze", retries=2, retry_delay_seconds=30)
def load_knmi_bronze():
    return docker_run("sentinel-pi-load-knmi-bronze:v1.0")


@task(name="load-zigbee-bronze", retries=2, retry_delay_seconds=30)
def load_zigbee_bronze():
    return docker_run("sentinel-pi-load-zigbee-bronze:v1.0")


@task(name="transform-knmi-silver", retries=2, retry_delay_seconds=30)
def transform_knmi_silver():
    return docker_run("sentinel-pi-transform-knmi-silver:v1.0")


@task(name="transform-zigbee-silver", retries=2, retry_delay_seconds=30)
def transform_zigbee_silver():
    return docker_run("sentinel-pi-transform-zigbee-silver:v1.0")


@task(name="transform-gold", retries=2, retry_delay_seconds=30)
def transform_gold():
    return docker_run("sentinel-pi-transform-gold:v1.0")


@task(name="ai-summary", retries=1, retry_delay_seconds=60)
def ai_summary():
    return docker_run(
        "sentinel-pi-ai-summary:v1.0",
        extra_flags=[
            "-v", "/mnt/data/sentinel-pi/docs:/mnt/data/sentinel-pi/docs",
            "--add-host", "host.docker.internal:host-gateway",
            "-e", "OLLAMA_URL=http://host.docker.internal:11434/api/generate",
        ]
    )


@flow(name="sentinel-pipeline", task_runner=ConcurrentTaskRunner())
def sentinel_pipeline():
    # # # Parallel collection
    # knmi = collect_knmi.submit()
    # zigbee = collect_zigbee.submit()
    # knmi_result = knmi.result()
    # zigbee_result = zigbee.result()

    # # # Parallel bronze load after respective collection
    # knmi_bronze = load_knmi_bronze.submit(knmi_result)
    # zigbee_bronze = load_zigbee_bronze.submit(zigbee_result)
    # knmi_bronze_result=knmi_bronze.result()
    # zigbee_bronze_result=zigbee_bronze.result()

    # # # Parallel silver transform after respective bronze
    # knmi_silver = transform_knmi_silver.submit(knmi_bronze_result)
    # zigbee_silver = transform_zigbee_silver.submit(zigbee_bronze_result)
    # knmi_silver_result=knmi_silver.result()
    # zigbee_silver_result=zigbee_silver.result()

    # # # # Gold needs both silver streams
    # gold = transform_gold.submit(knmi_silver_result, zigbee_silver_result)
    # gold_result=gold.result()

    # # # # AI after gold
    # ai_summary.submit(gold_result)

    collect_knmi()
    collect_zigbee()
    load_knmi_bronze()
    load_zigbee_bronze()
    transform_knmi_silver()
    transform_zigbee_silver()
    transform_gold()
    ai_summary() # need to check if running now for every 10 mins is creating locks. 


if __name__ == "__main__":
    sentinel_pipeline.serve(
        name="sentinel-pi-schedule",
        interval=timedelta(minutes=10)
    )
