from config import (
    BRONZE_LANDING,
    KNMI_BASE_URL
)
from knmi_utils import fetch_knmi_file
from datetime import datetime, timezone
from metrics_contract import KNMICollectMetrics
from pipeline_logger import write_jsonl_entry
import os
import logging
from openlineage_emitter import emit_lineage_event, get_run_id
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))


# KNMI modules


def collect_knmi():
    start_time = datetime.now(timezone.utc)
    logging.info("Starting KNMI data collection (Bronze)...")
    run_id = get_run_id()
    emit_lineage_event(
    job_name="collect_data_knmi",
    run_id=run_id,
    state="START",
    inputs=["KNMI API"],
    outputs=["bronze.landing"]
    )
    try:
        file_path = fetch_knmi_file(
            api_key=os.getenv("KNMI_API_KEY"),
            base_url=KNMI_BASE_URL,
            destination_dir=BRONZE_LANDING,
        )
        logging.info(f"KNMI raw file saved to: {file_path}")
        emit_lineage_event(
        job_name="collect_data_knmi",
        run_id=run_id,
        state="COMPLETE",
        inputs=["KNMI API"],
        outputs=["bronze.landing"]
        )
        write_jsonl_entry(
            stage="collect_knmi",
            status="success",
            start_time=start_time,
            metrics=KNMICollectMetrics(
                files_collected=1,
                api_calls_made=3
            )
        )
        return file_path
    except Exception as e:
        logging.error(f"KNMI collection failed: {str(e)}")
        emit_lineage_event(
        job_name="collect_data_knmi",
        run_id=run_id,
        state="FAIL",
        inputs=["KNMI API"],
        outputs=["bronze.landing"]
        )
        write_jsonl_entry(
            stage="collect_knmi",
            status="error",
            start_time=start_time,
            error=str(e)
        )
        raise


if __name__ == "__main__":
    # 1. Collect KNMI Raw files.
    knmi_file = collect_knmi()
