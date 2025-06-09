from typing import List
from pydantic.v1 import BaseSettings
from dotenv import load_dotenv
from random import randint
from os import getenv
from os.path import join, dirname

env_path = join(dirname(__file__), "../../.env")

# Load the environment variables from the .env file
load_dotenv(env_path)


class Environment(BaseSettings):
    # App settings
    API_VERSION: str = getenv("API_VERSION", "1")
    API_NAME: str = getenv("API_NAME", "LokaSync REST API")
    API_DESCRIPTION: str = getenv("API_DESCRIPTION", "LokaSync REST API for updating ESP firmware devices via Over-The-Air")

    # MongoDB settings
    MONGO_USERNAME: str = getenv("MONGO_USERNAME", "mongo_admin")
    MONGO_PASSWORD: str = getenv("MONGO_PASSWORD", "mongo_password")
    # Reference to the mongodb service name in docker-compose
    MONGO_HOST: str = getenv("MONGO_HOST", "mongodb")

    ### Uncomment the following lines if you want to use MongoDB in host machine
    # MONGO_HOST: str = getenv("MONGO_HOST", "localhost")
    # MONGO_PORT: int = int(getenv("MONGO_PORT", 27017))

    MONGO_DATABASE_NAME: str = getenv("MONGO_DATABASE_NAME", "app_db")

    # Construct the MongoDB connection URL
    if MONGO_USERNAME and MONGO_PASSWORD:
        MONGO_CONNECTION_URL: str = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DATABASE_NAME}?authSource=admin&retryWrites=true&w=majority"
    else:
        MONGO_CONNECTION_URL: str = f"mongodb://{MONGO_HOST}/{MONGO_DATABASE_NAME}?retryWrites=true&w=majority"

    # MQTT settings
    MQTT_BROKER_URL: str = getenv("MQTT_BROKER_URL", "broker.emqx.io")
    MQTT_BROKER_PORT: int = int(getenv("MQTT_BROKER_PORT", 1883))
    MQTT_BROKER_VERSION: str = getenv("MQTT_BROKER_VERSION", "3.1.1")
    MQTT_BROKER_KEEPALIVE: int = int(getenv("MQTT_BROKER_KEEPALIVE", 60))
    MQTT_BROKER_USERNAME: str = getenv("MQTT_BROKER_USERNAME", None)
    MQTT_BROKER_PASSWORD: str = getenv("MQTT_BROKER_PASSWORD", None)
    MQTT_BROKER_CA_CERT_NAME: str = getenv("MQTT_BROKER_CA_CERT_NAME", "emqxsl-ca.crt")
    MQTT_BROKER_TLS_ENABLED: bool = bool(getenv("MQTT_BROKER_TLS_ENABLED", False).capitalize())
    MQTT_SUBSCRIBE_TOPIC_LOG: str = getenv("MQTT_SUBSCRIBE_TOPIC_LOG", "OTAUpdate")
    MQTT_PUBLISH_TOPIC_LOG: str = getenv("MQTT_PUBLISH_TOPIC_LOG", "DisplayLog")
    MQTT_CLIENT_ID: str = getenv("MQTT_CLIENT_ID", f"lokasync_backend_{randint(1000, 9999)}")
    MQTT_DEFAULT_QOS: int = int(getenv("MQTT_DEFAULT_QOS", 1))

    # Firebase auth settings
    FIREBASE_CREDS_NAME: str = getenv("FIREBASE_CREDS_NAME", "firebase-credentials.json")

    # Google drive settings
    GOOGLE_DRIVE_MAX_FILE_SIZE_MB: int = int(getenv("GOOGLE_DRIVE_MAX_FILE_SIZE_MB", 3))
    GOOGLE_DRIVE_CREDS_NAME: str = getenv("GOOGLE_DRIVE_CREDS_NAME", "gdrive-credentials.json")
    GOOGLE_DRIVE_FOLDER_ID: str = getenv("GOOGLE_DRIVE_FOLDER_ID", None)

    # Timezone settings
    TIMEZONE: str = getenv("TIMEZONE", "Asia/Jakarta")


    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"
        case_sensitive = True


env = Environment()