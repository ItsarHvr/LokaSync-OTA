from fastapi import Depends
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from datetime import datetime, timezone

from cores.dependencies import get_db_connection, get_firmware_collection
from schemas.common import BaseFilterOptions
from models.firmware import FirmwareModel
from cores.config import env


class FirmwareRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        firmware_collection: AsyncIOMotorCollection = Depends(get_firmware_collection)
    ):
        self.db = db
        self.firmware_collection = firmware_collection
    
    async def get_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None,
        page: int = 1,
        page_size: int = 5
    ) -> List[FirmwareModel]:
        # Base query for filtering by parameters
        match_query = {}

        if node_id is not None:
            match_query["node_id"] = node_id
        if node_location is not None:
            match_query["node_location"] = node_location
        
        # MongoDB aggregation pipeline to get only the latest firmware version for each node
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": match_query},
            # Stage 2: Sort by node_id, node_location, node_name, and latest_updated
            {"$sort": {"node_id": 1, "node_location": 1, "node_name": 1, "latest_updated": -1}},
            # Stage 3: Group by node identifier and keep only the first (latest) document
            {"$group": {
                "_id": "$node_name",  # Group by node_name
                "doc": {"$first": "$$ROOT"}  # Keep the first document in each group (latest by updated date)
            }},
            # Stage 4: Replace the root with the original document
            {"$replaceRoot": {"newRoot": "$doc"}},
            # Stage 5: Sort results again by latest_updated for global ordering
            {"$sort": {"latest_updated": -1}},
            # Stage 6: Skip for pagination
            {"$skip": (page - 1) * page_size},
            # Stage 7: Limit results per page
            {"$limit": page_size}
        ]
    
        # Execute the aggregation pipeline
        cursor = self.firmware_collection.aggregate(pipeline)
        docs = await cursor.to_list(length=page_size)
        
        # Convert MongoDB documents to Firmware model objects
        return [
            FirmwareModel(
                id=str(doc["_id"]),
                firmware_description=doc.get("firmware_description", ""),
                firmware_version=doc["firmware_version"],
                firmware_url=doc["firmware_url"],
                latest_updated=doc["latest_updated"],
                node_id=doc["node_id"],
                node_location=doc["node_location"],
                node_name=doc["node_name"],
            )
            for doc in docs
        ]
    
    async def count_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None
    ) -> int:
        query = {}

        if node_id is not None:
            query["node_id"] = node_id
        if node_location is not None:
            query["node_location"] = node_location
        

        # MongoDB aggregation pipeline to count unique nodes
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": query},
            # Stage 2: Group by node identifier to get unique nodes
            {"$group": {"_id": "$node_name"}},
            # Stage 3: Count the number of unique nodes
            {"$count": "count"}
        ]

        # Execute the aggregation pipeline
        cursor = self.firmware_collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)

        # Return the count or 0 if no results
        return result[0]["count"] if result else 0
    
    async def get_filter_options(self) -> BaseFilterOptions:
        node_id = await self.firmware_collection.distinct("node_id")
        node_location = await self.firmware_collection.distinct("node_location")

        return BaseFilterOptions(
            node_id=node_id,
            node_location=node_location,
        )
    
    async def get_list_firmware_version(
        self,
        node_name: str,
    ) -> List[FirmwareModel]:
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": {"node_name": node_name}},
            # Stage 2: Sort by latest_updated
            {"$sort": {"latest_updated": -1}},
        ]

        cursor = self.firmware_collection.aggregate(pipeline)
        docs = await cursor.to_list()

        # Convert MongoDB documents to Firmware model objects
        return [
            FirmwareModel(
                id=str(doc["_id"]),
                firmware_description=doc.get("firmware_description", ""),
                firmware_version=doc["firmware_version"],
                firmware_url=doc["firmware_url"],
                latest_updated=doc["latest_updated"],
                node_id=doc["node_id"],
                node_location=doc["node_location"],
                node_name=doc["node_name"]
            )
            for doc in docs
        ]
    
    async def count_list_firmware_version(self, node_name: str) -> int:
        return await self.firmware_collection.count_documents({"node_name": node_name})
    
    async def add_new_node(self, firmware_data: dict):
        firmware_data["latest_updated"] = datetime.now(timezone.tzname(env.TIMEZONE))
        await self.firmware_collection.insert_one(firmware_data)
    
    async def update_firmware_version(self, node_name: str, firmware_data: dict):
        existing_data = await self.firmware_collection.find_one({"node_name": node_name})
        if not existing_data:
            return None
        
        new_firmware = {
            "node_id": existing_data["node_id"],
            "node_location": existing_data["node_location"],
            "node_name": node_name,
            "firmware_description": firmware_data.get("firmware_description", ""),
            "firmware_version": firmware_data["firmware_version"],
            "firmware_url": firmware_data["firmware_url"],
            "latest_updated": datetime.now(timezone.tzname(env.TIMEZONE)),
        }
        await self.firmware_collection.insert_one(new_firmware)
        return new_firmware
    
    async def update_firmware_description(
        self,
        node_name: str,
        firmware_version: str,
        firmware_data: dict
    ):
        existing_data = await self.firmware_collection.find_one({
            "node_name": node_name,
            "firmware_version": firmware_version,
        })
        if not existing_data:
            return None
        
        result = await self.firmware_collection.update_one(
            {
                "node_name": node_name,
                "firmware_version": firmware_version
            },
            {
                "$set": {
                    "firmware_description": firmware_data.get("firmware_description", ""),
                    "latest_updated": datetime.now(timezone.tzname(env.TIMEZONE))
                }
            }
        )

        return result.modified_count > 0
    
    async def delete_firmware_version(self, node_name: str, firmware_version: str):
        return await self.firmware_collection.delete_one({
            "node_name": node_name,
            "firmware_version": firmware_version
        })

    async def delete_all_version(self, node_name: str):
        return await self.firmware_collection.delete_many({
            "node_name": node_name
        })