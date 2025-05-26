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
    APP_VERSION: str = getenv("APP_VERSION", "1")
    APP_NAME: str = getenv("APP_NAME", "LokaSync REST API")
    APP_DESCRIPTION: str = getenv("APP_DESCRIPTION", "LokaSync REST API for updating ESP firmware devices via Over-The-Air")
    
    # MongoDB settings
    MONGO_DATABASE_NAME: str = getenv("MONGO_DATABASE_NAME", "lokasync_db")
    MONGO_CONNECTION_URL: str = getenv("MONGO_CONNECTION_URL", "mongodb://localhost:27017/")

    # MQTT settings
    MQTT_BROKER_URL: str = getenv("MQTT_BROKER_URL", "mqtt://localhost:1883")
    MQTT_BROKER_KEEPALIVE: int = int(getenv("MQTT_BROKER_KEEPALIVE", 60))
    MQTT_BROKER_PORT: int = int(getenv("MQTT_BROKER_PORT", 1883))
    MQTT_BROKER_USERNAME: str = getenv("MQTT_BROKER_USERNAME", None)
    MQTT_BROKER_PASSWORD: str = getenv("MQTT_BROKER_PASSWORD", None)
    MQTT_BROKER_CA_CERT_NAME: str = getenv("MQTT_BROKER_CA_CERT_NAME", "emqxsl-ca.crt")
    MQTT_BROKER_TLS_ENABLED: bool = getenv("MQTT_BROKER_TLS_ENABLED", "false").lower() in ("true", "1", "Yes")
    MQTT_PUBLISH_TOPIC_FIRMWARE: str = getenv("MQTT_PUBLISH_TOPIC_FIRMWARE")
    MQTT_SUBSCRIBE_TOPIC_LOG: str = getenv("MQTT_SUBSCRIBE_TOPIC_LOG")
    MQTT_CLIENT_ID: str = getenv("MQTT_CLIENT_ID", f"lokasync_backend_{randint(1000, 9999)}")
    MQTT_DEFAULT_QOS: int = int(getenv("MQTT_DEFAULT_QOS", 1))

    # Google Drive settings
    GOOGLE_DRIVE_CREDS_NAME: str = getenv("GOOGLE_DRIVE_CREDS_NAME")
    GOOGLE_DRIVE_FOLDER_ID: str = getenv("GOOGLE_DRIVE_FOLDER_ID")

    # Firebase auth settings
    FIREBASE_CREDS_NAME: str = getenv("FIREBASE_CREDS_NAME")

    # Middleware settings
    MIDDLEWARE_REQUEST_TIMEOUT_SECOND: float = float(getenv("MIDDLEWARE_REQUEST_TIMEOUT_SECOND", 30.0))
    MIDDLEWARE_REQUEST_TIMEOUT_SECOND_UPLOAD: float = float(getenv("MIDDLEWARE_REQUEST_TIMEOUT_SECOND_UPLOAD", 120.0))
    MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE: int = int(getenv("MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE", 10))
    MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR: int = int(getenv("MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR", 100))
    MIDDLEWARE_CORS_ALLOWED_ORIGINS: list[str] = getenv("MIDDLEWARE_CORS_ALLOWED_ORIGINS", "http://localhost,http://localhost:3000").split(",")

    # Timezone settings
    TIMEZONE: str = getenv("TIMEZONE", "Asia/Jakarta")


    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"
        case_sensitive = True


env = Environment()