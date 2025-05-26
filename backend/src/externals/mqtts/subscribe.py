import paho.mqtt.client as mqtt

from cores.config import env

def subscribe_message(client: mqtt.Client | None) -> None:
    def on_message(client, userdata, msg):
        print(f"✅ Subscribed to topic: {msg.topic} with QoS {msg.qos}")   
        print(f"🆗 Message received: {msg.payload.decode()}")
    
    client.subscribe(env.MQTT_SUBSCRIBE_TOPIC_LOG, qos=1)
    client.on_message = on_message