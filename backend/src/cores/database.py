from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from cores.config import env

client: AsyncIOMotorClient = AsyncIOMotorClient(env.MONGO_CONNECTION_URL)
_db: AsyncIOMotorDatabase = client[env.MONGO_DATABASE_NAME]

async def start_mongodb_connection() -> bool:
    """
    Check if the MongoDB connection is alive.
    """
    try:
        # Attempt to run a simple command to check the connection
        await _db.command("ping")
        return True
    except Exception:
        return False

async def stop_mongodb_connection() -> bool:
    """
    Close the MongoDB client connection.
    """
    try:
        await client.close()
        return True
    except Exception:
        return False