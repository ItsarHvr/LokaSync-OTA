from fastapi import Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from cores.dependencies import (
    get_db_connection,
    get_nodes_collection
)


class MonitoringRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        nodes_collection: AsyncIOMotorCollection = Depends(get_nodes_collection),
    ):
        self.db = db
        self.nodes_collection = nodes_collection
    
    async def get_list_nodes(self) -> List[str]:
        """
        Get a list of unique node locations, types, and IDs from the database.
        """
        node_locations = await self.nodes_collection.distinct("node_location")
        node_types = await self.nodes_collection.distinct("node_type")
        node_ids = await self.nodes_collection.distinct("node_id")

        return {
            "node_location": node_locations,
            "node_type": node_types,
            "node_id": node_ids
        }