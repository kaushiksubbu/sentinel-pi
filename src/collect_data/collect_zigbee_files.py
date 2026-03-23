# colect_zigbee_files.py
from datetime import datetime, timezone
from metrics_contract import ZigbeeCollectMetrics
from pipeline_logger import write_jsonl_entry
from logger import setup_log_dir
from dotenv import load_dotenv
from mqtt_client import create_long_lived_client, create_one_shot_client
import os
import time
import json
import logging
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))


# --- CHANGE THIS FLAG TO SWITCH BEHAVIOR ---
USE_ONE_SHOT = True  # True for cron; False for long‑lived process


# ---------- LOAD ENV VARIABLES ----------
load_dotenv()

BROKER = os.getenv("MQTT_BROKER")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPICS = os.getenv("MQTT_TOPICS", "").strip()
USERNAME = os.getenv("MQTT_USER")
PASSWORD = os.getenv("MQTT_PASS")


# ---------- PATHS ----------
BRONZE_LANDING = "/mnt/data/sentinel-pi/data/bronze/landing_zone"
LOG_DIR = "/mnt/data/sentinel-pi/logs"

os.makedirs(BRONZE_LANDING, exist_ok=True)
log_file = setup_log_dir(LOG_DIR, log_filename="cron.log")


# Parse MQTT_TOPICS
try:
    if not TOPICS:
        error_msg = "Error - MQTT_TOPICS is empty or not set in .env"
        logging.error(error_msg)
        raise ValueError(error_msg)

    ZIGBEE_TOPICS = [t.strip() for t in TOPICS.split(",") if t.strip()]

    if not ZIGBEE_TOPICS:
        error_msg = "Error - No valid topics found in MQTT_TOPICS after parsing"
        logging.error(error_msg)
        raise ValueError(error_msg)

except Exception as e:
    logging.error(f"Error - Error parsing MQTT_TOPICS from .env: {e}")
    raise


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        logging.error(f"Error connecting to MQTT Broker: {reason_code}")
    else:
        logging.info("Connected to MQTT Broker.")
        for t in ZIGBEE_TOPICS:
            client.subscribe(t)


if __name__ == "__main__":
    start_time = datetime.now(timezone.utc)

    client = (
        create_one_shot_client(
            broker=BROKER,
            port=PORT,
            landing_dir=BRONZE_LANDING,
            log_file=log_file,
            username=USERNAME,
            password=PASSWORD,
        )
        if USE_ONE_SHOT
        else create_long_lived_client(
            broker=BROKER,
            port=PORT,
            landing_dir=BRONZE_LANDING,
            log_file=log_file,
            username=USERNAME,
            password=PASSWORD,
        )
    )

    client.on_connect = on_connect

    try:
        client.connect(BROKER, PORT, 60)

        if USE_ONE_SHOT:
            client.loop_start()
            time.sleep(5 * 60)
            client.loop_stop()
            client.disconnect()

            total_files = 0
            total_messages = 0

            for topic, records in client.all_messages.items():
                safe_topic = topic.replace("/", "_").replace(" ", "_")
                filename = os.path.join(
                    BRONZE_LANDING,
                    f"zigbee_{safe_topic}_{datetime.now().strftime('%Y%m%d%H')}.json"
                )
                with open(filename, "w") as f:
                    json.dump({
                        "topic": topic,
                        "messages": records,
                        "window_start": records[0]["timestamp"] if records else None,
                        "window_end": datetime.now().isoformat(),
                    }, f, indent=2, ensure_ascii=False)

                logging.info(
                    f"Saved {len(records)} messages for {topic} to {filename}")
                total_files += 1
                total_messages += len(records)

            # ONE entry for the whole run — after the loop
            write_jsonl_entry(
                stage="collect_zigbee",
                status="success",
                start_time=start_time,
                metrics=ZigbeeCollectMetrics(
                    files_collected=total_files,
                    messages_received=total_messages
                )
            )
        else:
            client.loop_forever()

    except Exception as e:
        logging.error(f"Error in MQTT client run: {e}")
        write_jsonl_entry(
            stage="collect_zigbee",
            status="error",
            start_time=start_time,
            error=str(e)
        )
        raise
