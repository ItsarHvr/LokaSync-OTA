from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = AsyncIOMotorClient(MONGO_URL)
mongo_db = client[MONGO_DB_NAME]
firmware_collection = mongo_db["firmware"]
log_collection = mongo_db["log"]

def get_log_collection():
    return log_collection

def get_firmware_collection():
    return firmware_collection