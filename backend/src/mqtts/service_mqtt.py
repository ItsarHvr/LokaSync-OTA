# import json
# import paho.mqtt.client as mqtt
# import threading
# import asyncio
# import os
# from dotenv import load_dotenv

# from dtos.dto_log import InputLog
# from repositories.repository_log import LogRepository

# load_dotenv()

# BROKER_ADDRESS = getenv("MQTT_ADDRESS")
# BROKER_PORT = int(getenv("MQTT_PORT"))

# TOPICS = [
#     ("OTA/Node-DHT", 0),
#     ("Pollux/log/Firmware_Update", 0),
#     ("OTA/Water_Node", 0),
#     ("LokaSync/CloudOTA/Firmware", 0)
# ]

# loop = asyncio.get_event_loop()

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))
#     for topic, qos in TOPICS:
#         client.subscribe(topic)
#         print(f"Subscribed to {topic}")

# def on_message(client, userdata, msg):
#     print(f"Received message on {msg.topic}: {msg.payload.decode()}")
#     try:
#         data = json.loads(msg.payload.decode())
#         topic = msg.topic

#         if topic == "Pollux/log/Firmware_Update":
#             asyncio.run_coroutine_threadsafe(add_log(data), loop)
                        
#         elif topic == "Pollux/log/Firmware":
#             pass
#         elif topic == "sensor/temperature":
#             pass
#     except Exception as e:
#         print("MQTT Data Error", e)

# async def add_log(payload: dict):
#     repository_mqtt_log = LogRepository()
#     required_keys = ["node_name", "node_location", "node_status", "first_version", "latest_version"]
#     if all(k in payload for k in required_keys):
#         node_status = True if payload["node_status"] == "active" else False

#         input_log = InputLog(
#             node_location=payload["node_location"],
#             node_status=node_status,
#             first_version=payload["first_version"],
#             latest_version=payload["latest_version"]
#         )
#         await repository_mqtt_log.add_log(input_log, node_name=payload["node_name"])
#     else:
#         print("Payload tidak valid atau field kurang")


# def start_mqtt():
#     client = mqtt.Client()
#     client.on_connect = on_connect
#     client.on_message = on_message

#     client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

#     thread = threading.Thread(target=client.loop_forever, name="MQTTThread")
#     thread.daemon = True
#     thread.start()
