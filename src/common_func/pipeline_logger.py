# pipeline_logger.py
import os
from config import STRUCTURED_LOG_FILE, JSONL_RUNS_TO_READ, JSONL_LINES_PER_RUN
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import sys
sys.path.insert(0, "/home/kaushik/sentinel-pi/src/common_func")


def write_jsonl_entry(stage: str,
                      status: str,
                      start_time: datetime,
                      metrics: dict = None,
                      dq_failed_reason: str = None,
                      error: str = None):
    try:
        run_name = os.getenv("PREFECT_RUN_NAME", None)
    except Exception:
        run_name = None
#          "run_id": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
#        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
#        "end_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    entry = {
        "run_id": start_time.astimezone(ZoneInfo("Europe/Amsterdam"))
                            .strftime("%Y-%m-%dT%H:%M:%S"),
        "run_name": run_name,
        "stage": stage,
        "status": status,
        "start_time": start_time.replace(tzinfo=timezone.utc)
                                .astimezone(ZoneInfo("Europe/Amsterdam"))
                                .strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": datetime.now(timezone.utc)
                            .astimezone(ZoneInfo("Europe/Amsterdam"))
                            .strftime("%Y-%m-%dT%H:%M:%S"),
        "metrics": metrics or {},
        "dq_failed_reason": dq_failed_reason,
        "error": error
    }

    with open(STRUCTURED_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_recent_jsonl():
    lines_to_read = JSONL_RUNS_TO_READ * JSONL_LINES_PER_RUN
    path = Path(STRUCTURED_LOG_FILE)
    if not path.exists():
        return []
    with open(path, "r") as f:
        all_lines = f.readlines()
    return [json.loads(line) for line in all_lines[-lines_to_read:]]
    