from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from cores.config import env
from utils.logger import logger

client: AsyncIOMotorClient = AsyncIOMotorClient(env.MONGO_CONNECTION_URL)
_db: AsyncIOMotorDatabase = client[env.MONGO_DATABASE_NAME]

async def start_mongodb_connection() -> bool:
    """
    Check if the MongoDB connection is alive.
    """
    try:
        # Attempt to run a simple command to check the connection
        await _db.command("ping")
        logger.db_info("MongoDB connection established successfully")
        return True
    except Exception as e:
        logger.db_error(f"Failed to connect to MongoDB: {str(e)}")
        return False

async def stop_mongodb_connection() -> bool:
    """
    Close the MongoDB client connection.
    """
    try:
        client.close()
        logger.db_info("MongoDB connection closed successfully")
        return True
    except Exception as e:
        logger.db_error(f"Failed to close MongoDB connection: {str(e)}")
        return False