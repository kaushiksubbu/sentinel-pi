# mqtt_client.py
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os
from logger import log


def create_long_lived_client(
    broker: str,
    port: int,
    landing_dir: str,
    log_file: str,
    username: str = None,
    password: str = None,
) -> mqtt.Client:
    """
    Returns a long‑lived MQTT client that can stay connected for hours/days.
    Suitable for services, not for cron.
    """
    os.makedirs(landing_dir, exist_ok=True)

    def on_message(client, userdata, msg):
        try:
            payload = msg.payload.decode()
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = {"raw": payload}
        except Exception:
            data = {"raw": str(msg.payload)}

        record = {
            "topic": msg.topic,
            "payload": data,
            "timestamp": datetime.now().isoformat(),
        }

        safe_topic = msg.topic.replace("/", "_").replace(" ", "_")
        filename = os.path.join(landing_dir, f"zigbee_{safe_topic}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")

        with open(filename, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        log(f"Saved message to {filename} (topic: {msg.topic})", log_file)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    if username and password:
        client.username_pw_set(username=username, password=password)

    return client

def create_one_shot_client(
    broker: str,
    port: int,
    landing_dir: str,
    log_file: str,
    username: str = None,
    password: str = None,
    snapshot_duration: float = 300.0,  # 5 minutes
):
    os.makedirs(landing_dir, exist_ok=True)

    # All messages per topic
    all_messages = {}  # topic -> list of records

    def on_message(client, userdata, msg):
        try:
            payload = msg.payload.decode()
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = {"raw": payload}
        except Exception:
            data = {"raw": str(msg.payload)}

        record = {
            "topic": msg.topic,
            "payload": data,
            "timestamp": datetime.now().isoformat(),
        }

        # Initialize list for topic
        if msg.topic not in all_messages:
            all_messages[msg.topic] = []
        all_messages[msg.topic].append(record)

        log(f"Collected message for {msg.topic} (5‑minute window)", log_file)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    if username and password:
        client.username_pw_set(username=username, password=password)

    client.all_messages = all_messages   # expose to zigbee_ingest.py
    client.snapshot_duration = snapshot_duration

    return client

