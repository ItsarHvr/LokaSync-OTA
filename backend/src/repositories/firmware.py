import asyncio
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
        page: int = 1,
        page_size: int = 10,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None
    ) -> List[FirmwareModel]:
        """Get latest firmware version for each node with pagination."""
        match_query = self._build_query(node_id, node_location)
        
        pipeline = [
            {"$match": match_query},
            {"$sort": {"node_name": 1, "latest_updated": -1}},
            {"$group": {
                "_id": "$node_name",
                "doc": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$doc"}},
            {"$sort": {"latest_updated": -1}},
            {"$skip": (page - 1) * page_size},
            {"$limit": page_size}
        ]
        
        cursor = self.firmware_collection.aggregate(pipeline)
        docs = await cursor.to_list(length=page_size)
        
        return [self._doc_to_model(doc) for doc in docs]
    
    async def count_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None
    ) -> int:
        """Count unique nodes with filters."""
        match_query = self._build_query(node_id, node_location)
        
        pipeline = [
            {"$match": match_query},
            {"$group": {"_id": "$node_name"}},
            {"$count": "count"}
        ]
        
        cursor = self.firmware_collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        return result[0]["count"] if result else 0
    
    async def get_filter_options(self) -> BaseFilterOptions:
        """Get available filter options."""
        node_id, node_location = await asyncio.gather(
            self.firmware_collection.distinct("node_id"),
            self.firmware_collection.distinct("node_location")
        )
        
        return BaseFilterOptions(
            node_id=sorted(node_id),
            node_location=sorted(node_location)
        )
    
    async def get_list_firmware_version(self, node_name: str) -> List[FirmwareModel]:
        """Get all firmware versions for a specific node."""
        pipeline = [
            {"$match": {"node_name": node_name}},
            {"$sort": {"latest_updated": -1}}
        ]
        
        cursor = self.firmware_collection.aggregate(pipeline)
        docs = await cursor.to_list()
        
        return [self._doc_to_model(doc) for doc in docs]
    
    async def add_new_node(self, firmware_data: dict) -> str:
        """Add new firmware document."""
        firmware_data["created_at"] = datetime.now(timezone.tzname(env.TIMEZONE))
        firmware_data["latest_updated"] = datetime.now(timezone.tzname(env.TIMEZONE))
        
        result = await self.firmware_collection.insert_one(firmware_data)
        return str(result.inserted_id)
    
    async def update_firmware_version(self, node_name: str, firmware_data: dict) -> Optional[dict]:
        """Add new firmware version for existing node."""
        existing_data = await self.firmware_collection.find_one(
            {"node_name": node_name},
            sort=[("latest_updated", -1)]
        )
        
        if not existing_data:
            return None
        
        new_firmware = {
            "node_id": existing_data["node_id"],
            "node_location": existing_data["node_location"],
            "node_name": node_name,
            "firmware_description": firmware_data.get("firmware_description", ""),
            "firmware_version": firmware_data["firmware_version"],
            "firmware_url": firmware_data["firmware_url"],
            "created_at": datetime.now(timezone.tzname(env.TIMEZONE)),
            "latest_updated": datetime.now(timezone.tzname(env.TIMEZONE)),
        }
        
        result = await self.firmware_collection.insert_one(new_firmware)
        new_firmware["_id"] = result.inserted_id
        return new_firmware
    
    async def update_firmware_description(
        self,
        node_name: str,
        firmware_version: str,
        firmware_data: dict
    ) -> bool:
        """Update firmware description for specific version."""
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
        """Delete specific firmware version."""
        return await self.firmware_collection.delete_one({
            "node_name": node_name,
            "firmware_version": firmware_version
        })
    
    async def delete_all_version(self, node_name: str):
        """Delete all firmware versions for a node."""
        return await self.firmware_collection.delete_many({
            "node_name": node_name
        })
    
    async def firmware_exists(self, node_name: str, firmware_version: str) -> bool:
        """Check if firmware version exists."""
        count = await self.firmware_collection.count_documents({
            "node_name": node_name,
            "firmware_version": firmware_version
        })
        return count > 0
    
    # Helper methods
    def _build_query(self, node_id: Optional[int], node_location: Optional[str]) -> dict:
        """Build MongoDB query from filters."""
        query = {}
        if node_id is not None:
            query["node_id"] = node_id
        if node_location is not None:
            query["node_location"] = node_location
        return query
    
    def _doc_to_model(self, doc: dict) -> FirmwareModel:
        """Convert MongoDB document to FirmwareModel."""
        return FirmwareModel(
            id=str(doc["_id"]),
            created_at=doc.get("created_at", datetime.now(timezone.tzname(env.TIMEZONE))),
            firmware_description=doc.get("firmware_description", ""),
            firmware_version=doc["firmware_version"],
            firmware_url=doc["firmware_url"],
            latest_updated=doc["latest_updated"],
            node_id=doc["node_id"],
            node_location=doc["node_location"],
            node_name=doc["node_name"]
        )