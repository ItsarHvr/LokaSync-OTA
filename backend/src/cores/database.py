from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from motor.motor_asyncio import AsyncIOMotorCollection

from cores.config import env

client: AsyncIOMotorClient = AsyncIOMotorClient(env.MONGO_CONNECTION_URL)
db: AsyncIOMotorDatabase = client[env.MONGO_DATABASE_NAME]
firmware_collection: AsyncIOMotorCollection = db["firmware"]
log_collection: AsyncIOMotorCollection = db["log"]

async def start_mongodb_connection() -> bool:
    """
    Check if the MongoDB connection is alive.
    """
    try:
        # Attempt to run a simple command to check the connection
        await db.command("ping")
        return True
    except Exception as e:
        return False

async def stop_mongodb_connection() -> bool:
    """
    Close the MongoDB client connection.
    """
    try:
        await client.close()
        return True
    except Exception as e:
        return False