from externals.mqtts.client import mqtt
from cores.config import env
from utils.logger import logger
from utils.datetime import json_dumps_with_datetime

"""NOTE:
After saving the log data to MongoDB,
then publish the log data to the frontend.
"""
def publish_log_data(client: mqtt.Client | None, log_data: dict) -> bool:
    if client is None or not client.is_connected():
        logger.mqtt_error("Cannot publish log data: MQTT client not connected.")
        return False
    
    PUB_TOPIC_LOG = env.MQTT_PUBLISH_TOPIC_LOG
    
    try:
        # Convert dict to JSON string
        payload = json_dumps_with_datetime(log_data)

        # Publish with QoS 1 to ensure delivery
        logger.mqtt_info(f"Publishing log data to {PUB_TOPIC_LOG}")
        client.publish(
            topic=PUB_TOPIC_LOG,
            payload=payload,
            qos=env.MQTT_DEFAULT_QOS
        )
        logger.mqtt_info(f"Successfully published log data to {PUB_TOPIC_LOG}")
        return True
    except Exception as e:
        logger.mqtt_error(f"Failed to publish log data to {PUB_TOPIC_LOG}", e)
        return False


"""NOTE:
After saving the data sensor to MongoDB,
then publish the data sensor to the frontend.
"""
def publish_sensor_data(
  client: mqtt.Client | None,
  sensor_data: dict
):
    PUB_TOPIC_MONITORING = env.MQTT_PUBLISH_TOPIC_MONITORING
    return