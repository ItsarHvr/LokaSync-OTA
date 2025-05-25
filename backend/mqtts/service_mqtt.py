import json
import paho.mqtt.client as mqtt
import threading
import asyncio
import os
from dotenv import load_dotenv

from dtos.dto_log import InputLog
from repositories.repository_log import LogRepository
from databases.mongodb import get_log_collection

load_dotenv()

BROKER_ADDRESS = os.getenv("MQTT_ADDRESS")
BROKER_PORT = int(os.getenv("MQTT_PORT"))

TOPICS = [
    ("LokaSync/CloudOTA/Log", 0),
    ("LokaSync/CloudOTA/Firmware", 0)
]

loop = asyncio.get_event_loop()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic, qos in TOPICS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    payload_raw = msg.payload.decode()
    topic = msg.topic

    print(f"[MQTT] Received on {topic}: {payload_raw}")

    try:
        data = json.loads(payload_raw)

        if topic == "LokaSync/CloudOTA/Log":
            asyncio.run_coroutine_threadsafe(add_log(data), loop)
        elif topic == "LokaSync/CloudOTA/Firmware":
            pass
        else:
            print(f"[MQTT] unhandled topic: {topic}")
    except json.JSONDecodeError:
        print(f"[MQTT] Invalid JSON format on topic {topic}")        
    except Exception as e:
        print(f"[MQTT] Error processing message from {topic}")

async def add_log(payload: dict):
    try:
        required_keys = ["type", "message", "node_name", "firmware_version"]
        if not all(k in payload for k in required_keys):
            print(f"[MQTT] Incomplete payload: {payload}")
            return
        
        payload.pop("timestamp", None)

        input_log = InputLog(**payload)

        repo = LogRepository(get_log_collection())
        result = await repo.add_log(input_log)

        print(f"[MQTT] Log added: {result}")

    except Exception as e:
        print(f"[MQTT] Failed to insert log: {e} | Payload: {payload}")


def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

    thread = threading.Thread(target=client.loop_forever, name="MQTTThread")
    thread.daemon = True
    thread.start()
