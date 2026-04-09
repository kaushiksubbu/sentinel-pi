# Version 1 - Base version - trial for parallel runs
# version 2 - commented out - trailed ffailed - set all flows as seq.
# version 3 - commented out - AI as this was causing an overspill schedule time
# version 4 - New flow to modularize collection, writes and AI flow.
import sys
import subprocess
from datetime import timedelta  # noqa: F401
from dotenv import load_dotenv
from prefect import flow, task, serve
from prefect.runtime import flow_run


load_dotenv("/mnt/data/sentinel-pi/.env")

VENV_PYTHON = sys.executable


def docker_run(image: str, extra_flags: list = []):
    run_name = flow_run.name or "unscheduled"
    cmd = [
        "docker", "run", "--rm",
        "--pull", "never",
        "-v", "/mnt/data/sentinel-pi/src:/mnt/data/sentinel-pi/src",
        "-v", "/mnt/data/sentinel-pi/data:/mnt/data/sentinel-pi/data",
        "-v", "/mnt/data/sentinel-pi/logs:/mnt/data/sentinel-pi/logs",
        "-e", "TZ=Europe/Amsterdam",
        "-e", f"PREFECT_RUN_NAME={run_name}",
        "--env-file", "/mnt/data/sentinel-pi/.env",
    ] + extra_flags + [image]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"{image} failed:\n{result.stderr}")
    return result.stdout


# ── Tasks ──────────────────────────────────────────────

@task(name="collect-knmi", retries=2, retry_delay_seconds=30)
def collect_knmi():
    return docker_run("sentinel-pi-collect-knmi:latest")


@task(name="collect-zigbee", retries=2, retry_delay_seconds=30)
def collect_zigbee():
    return docker_run("sentinel-pi-collect-zigbee:latest")


@task(name="load-knmi-bronze", retries=2, retry_delay_seconds=30)
def load_knmi_bronze():
    return docker_run("sentinel-pi-load-knmi-bronze:latest")


@task(name="load-zigbee-bronze", retries=2, retry_delay_seconds=30)
def load_zigbee_bronze():
    return docker_run("sentinel-pi-load-zigbee-bronze:latest")


@task(name="transform-knmi-silver", retries=2, retry_delay_seconds=30)
def transform_knmi_silver():
    return docker_run("sentinel-pi-transform-knmi-silver:latest")


@task(name="transform-zigbee-silver", retries=2, retry_delay_seconds=30)
def transform_zigbee_silver():
    return docker_run("sentinel-pi-transform-zigbee-silver:latest")


@task(name="transform-gold", retries=2, retry_delay_seconds=30)
def transform_gold():
    return docker_run("sentinel-pi-transform-gold:latest")


@task(name="ai-summary", retries=1, retry_delay_seconds=60)
def ai_summary():
    return docker_run(
        "sentinel-pi-ai-summary:latest",
        extra_flags=[
            "-v", "/mnt/data/sentinel-pi/docs:/mnt/data/sentinel-pi/docs",
            "--add-host", "host.docker.internal:host-gateway",
            "-e", "OLLAMA_URL=http://host.docker.internal:11434/api/generate",
        ]
    )


# ── Flows ──────────────────────────────────────────────

@flow(name="collect-knmi-flow")
def collect_knmi_flow():
    """
    Collects KNMI data only.
    Schedule: every 10 mins — matches KNMI publish frequency.
    Producer cadence respected: KNMI publishes 6 files/hour.
    """
    collect_knmi()


@flow(name="collect-zigbee-flow")
def collect_zigbee_flow():
    """
    Collects Zigbee MQTT data only.
    Schedule: every 6 mins — MQTT window is 5 mins + 1 min gap.
    """
    collect_zigbee()


@flow(name="load-transform-flow")
def load_transform_flow():
    """
    Loads Bronze and transforms to Silver and Gold.
    Schedule: every 10 mins — watermark-driven, safe to run
    independently of collection timing.
    """
    load_knmi_bronze()
    load_zigbee_bronze()
    transform_knmi_silver()
    transform_zigbee_silver()
    transform_gold()


@flow(name="ai-summary-flow")
def ai_summary_flow():
    """
    AI daily summary — reads last 6 pipeline runs (1 hour).
    Schedule: every 60 mins — decoupled from pipeline contention.
    JSONL_RUNS_TO_READ=6 in config.py covers 6 x 10-min windows.
    """
    ai_summary()


# ── Serve ──────────────────────────────────────────────

if __name__ == "__main__":
    # Flows are triggered by cron via prefect deployment run
    # See crontab for schedule configuration
    # pass
    # serve() removed — unstable on Pi with 4 concurrent schedules
    # added back to test
    serve(
        collect_knmi_flow.to_deployment(
            name="collect-knmi-schedule"
        ),
        collect_zigbee_flow.to_deployment(
            name="collect-zigbee-schedule"
        ),
        load_transform_flow.to_deployment(
            name="load-transform-schedule"
        ),
        ai_summary_flow.to_deployment(
            name="ai-summary-schedule"
        ),
    )
