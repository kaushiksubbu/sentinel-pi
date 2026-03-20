import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import json

load_dotenv()  # reads .env and sets environment variables

topics = [
    'zigbee2mqtt/Bedroom1 T&H',
    'zigbee2mqtt/Attic T&H',
    'zigbee2mqtt/Bedroom2 T&H',
    'zigbee2mqtt/Hall T&H',
    'zigbee2mqtt/Bath T&H'
]

def on_connect(client, userdata, flags, reason_code, properties):
    print("TEST CONNECT: inside on_connect")
    print("Reason code:", reason_code)
    if reason_code.is_failure:
        print("FAILED:", reason_code)
    else:
        print("Connected OK")
        for topic in topics:
            client.subscribe(topic)

def on_message(client, userdata, msg): 
    print("Topic:", msg.topic)
    print("Payload:", msg.payload.decode())

USERNAME = os.getenv("MQTT_USER")
PASSWORD = os.getenv("MQTT_PASS")

print("Using user:", USERNAME)  # sanity check

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.68.55", 1883, 60)
client.loop_forever()
