# openlineage_emitter.py
# Emits OpenLineage events to JSONL file.
# Marquez deferred — ARM64 constraint (ADR-049).
# Events written to lineage/openlineage_events.jsonl
# Non-blocking — pipeline never fails due to lineage.

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from config import LINEAGE_FILE, NAMESPACE

# LINEAGE_FILE = "/mnt/data/sentinel-pi/logs/openlineage_events.jsonl"
# NAMESPACE = "sentinel-pi"


def get_run_id() -> str:
    """Stable run ID from Prefect run name if available."""
    prefect_run = os.getenv("PREFECT_RUN_NAME", None)
    if prefect_run:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, prefect_run))
    return str(uuid.uuid4())


def emit_lineage_event(
    job_name: str,
    run_id: str,
    state: str,
    inputs: list = None,
    outputs: list = None,
):
    """
    Writes OpenLineage event to JSONL file.
    state: START or COMPLETE or FAIL
    inputs/outputs: list of dataset name strings
    Fails silently — pipeline never blocked by lineage.
    """
    try:
        os.makedirs(os.path.dirname(LINEAGE_FILE), exist_ok=True)

        event = {
            "eventType": state,
            "eventTime": datetime.now(timezone.utc).isoformat(),
            "run": {"runId": run_id},
            "job": {
                "namespace": NAMESPACE,
                "name": job_name
            },
            "inputs": inputs or [],
            "outputs": outputs or [],
            "producer": "sentinel-pi/pipeline"
        }

        with open(LINEAGE_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")

        logging.info(f"Lineage emitted | {job_name} | {state}")

    except Exception as e:
        logging.warning(f"Lineage emission failed silently | {e}")
