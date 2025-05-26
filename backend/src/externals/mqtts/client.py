import paho.mqtt.client as mqtt
from os.path import join, dirname

from cores.config import env

ca_cert = join(dirname(__file__), "../../../", env.MQTT_BROKER_CA_CERT_NAME)

def check_mqtt_credentials(ca_cert: str) -> bool:
    """
    Check if the MQTT broker CA certificate file exists.
    """
    try:
        with open(ca_cert, 'r'):
            print("✅ MQTT broker CA certificate file found.")

        return True
    except FileNotFoundError:
        print(f"❌ MQTT broker CA certificate file not found: {ca_cert}")
        return False

def connect_mqtt_client() -> mqtt.Client | None:
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ Connected to MQTT Broker!")
        else:
            print(f"❌ Failed to connect, return code: {rc}\n")

    def on_disconnect(client, userdata, rc, properties=None, reason_code=None):
        if rc != 0:
            print("❌ Unexpected disconnection from MQTT Broker!")
        else:
            print("✅ Disconnected from MQTT Broker.")
    
    try:
        client = mqtt.Client(
            client_id=env.MQTT_CLIENT_ID,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2 # For paho-mqtt >= 1.6.0
        )
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        if env.MQTT_BROKER_TLS_ENABLED and check_mqtt_credentials(ca_cert):
            client.tls_set(ca_cert)
        
        if not env.MQTT_BROKER_TLS_ENABLED and not check_mqtt_credentials(ca_cert):
            client.tls_insecure_set(True)  # Allow insecure connection if TLS is not enabled
        
        if env.MQTT_BROKER_USERNAME and env.MQTT_BROKER_PASSWORD:
            client.username_pw_set(
                username=env.MQTT_BROKER_USERNAME,
                password=env.MQTT_BROKER_PASSWORD
            )

        client.connect(
            host=env.MQTT_BROKER_URL,
            port=env.MQTT_BROKER_PORT,
            keepalive=env.MQTT_BROKER_KEEPALIVE
        )
    
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MQTT Broker: {str(e)}")
        return None