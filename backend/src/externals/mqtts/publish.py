import paho.mqtt.client as mqtt
from time import sleep

from cores.config import env

def publish_message(client: mqtt.Client | None) -> None:
    result = client.publish(
        env.MQTT_PUBLISH_TOPIC_FIRMWARE,
        payload="Hello, MQTT!"
    )

    status = result.rc
    if status == mqtt.MQTT_ERR_SUCCESS:
        print(f"🆗 Message published to topic {env.MQTT_PUBLISH_TOPIC_FIRMWARE}")
    else:
        print(f"❌ Failed to publish message, return code: {status}")