import paho.mqtt.client as mqtt
import asyncio
import time

from externals.mqtts.client import connect_mqtt_client
from externals.mqtts.subscribe import subscribe_message
from utils.logger import logger

_mqtt_client_instance: mqtt.Client | None = connect_mqtt_client()

def start_mqtt_service(main_loop: asyncio.AbstractEventLoop = None) -> bool:
    """
    Connects to MQTT, starts its loop in a background thread, and subscribes to topics.
    Returns True if successful, False otherwise.
    """
    global _mqtt_client_instance
    if _mqtt_client_instance is not None:
        _mqtt_client_instance.loop_start()        # Wait for the MQTT client to connect to the broker
        for _ in range(10):  # max ~5 seconds
            if _mqtt_client_instance.is_connected():
                break
            time.sleep(0.5)
        
        if _mqtt_client_instance.is_connected():
            subscribe_message(_mqtt_client_instance, main_loop)
            logger.mqtt_info("MQTT service started successfully")
            return True
        
        logger.mqtt_error("Failed to connect to MQTT Broker within the timeout period")
        return False
        
    return False

def stop_mqtt_service() -> bool:
    """
    Stops the MQTT client loop and disconnects the client.
    """
    global _mqtt_client_instance
    if _mqtt_client_instance:
        _mqtt_client_instance.loop_stop()
        _mqtt_client_instance.disconnect()
        return True
    return False

def get_mqtt_client() -> mqtt.Client | None:
    """
    Returns the MQTT client instance.
    """
    return _mqtt_client_instance