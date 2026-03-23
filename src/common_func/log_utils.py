import logging
import json
from datetime import datetime, timezone
from config import STRUCTURED_LOG_FILE


def log_event(
    level: str,
    component: str,
    message: str,
    metrics: dict = None
):
    """
    Single entry point for all platform logging.
    Writes to:
      1. cron.log       -> human readable (via logging module)
      2. pipeline.jsonl -> structured JSON per event

    Usage:
        log_event("INFO", "Gold", "Transform complete",
                  {"total": 16, "valid": 16, "invalid": 0})
    """
    # Human readable
    log_msg = f"{component} | {message}"
    if metrics:
        log_msg += " | " + " | ".join(
            f"{k}: {v}" for k, v in metrics.items()
        )

    if level == "INFO":
        logging.info(log_msg)
    elif level == "WARNING":
        logging.warning(log_msg)
    elif level == "ERROR":
        logging.error(log_msg)

    # Structured JSON
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "component": component,
        "message": message,
        "metrics": metrics or {}
    }
    with open(STRUCTURED_LOG_FILE, 'a') as f:
        f.write(json.dumps(event) + "\n")
