from fastapi import Depends
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from cores.dependencies import (
    get_db_connection,
    get_nodes_collection
)
from utils.logger import logger


class MonitoringRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        nodes_collection: AsyncIOMotorCollection = Depends(get_nodes_collection),
    ):
        self.db = db
        self.nodes_collection = nodes_collection
    
    async def get_list_nodes(self) -> Dict[str, List[str]]:
        """
        Get list of node locations, types, and IDs.
        """
        logger.db_info("Repository: Getting list of distinct node values")
        
        try:
            node_locations = sorted(await self.nodes_collection.distinct("node_location"))
            node_types = sorted(await self.nodes_collection.distinct("node_type"))
            node_ids = sorted(await self.nodes_collection.distinct("node_id"))

            if not node_locations and not node_types and not node_ids:
                logger.db_info("Repository: No nodes found in collection")
                return {
                    "node_locations": [],
                    "node_types": [],
                    "node_ids": []
                }

            result = {
                "node_locations": node_locations,
                "node_types": node_types,
                "node_ids": node_ids
            }
            
            logger.db_info(f"Repository: Retrieved distinct values - Locations: {len(node_locations)}, Types: {len(node_types)}, IDs: {len(node_ids)}")
            return result
            
        except Exception as e:
            logger.db_error("Repository: Failed to get list of nodes", e)
            return {
                "node_locations": [],
                "node_types": [],
                "node_ids": []
            }