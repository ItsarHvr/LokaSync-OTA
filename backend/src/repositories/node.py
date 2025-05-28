from fastapi import Depends
from fastapi.exceptions import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import ASCENDING
from typing import List, Dict, Any, Optional
from datetime import datetime

from cores.dependencies import get_db_connection, get_nodes_collection
from models.node import NodeModel
from schemas.common import BaseFilterOptions
from schemas.node import NodeCreateSchema
from utils.datetime import set_default_timezone
from utils.validator import set_codename


class NodeRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        nodes_collection: AsyncIOMotorCollection = Depends(get_nodes_collection)
    ):
        self.db = db
        self.nodes_collection = nodes_collection

    async def add_node_location(self, node_data: NodeCreateSchema) -> NodeModel:
        """
        Create a new node location (document) in the database.
            Added fields to document NodeModel:
                - node_location: str
                - node_type: str
                - node_id: str
                - node_codename: str
                - description: Optional[str]
        
        Method: POST (creating new document)
        """
        node_location: str = node_data.node_location
        node_type: str = node_data.node_type
        node_id: str = node_data.node_id
        node_codename: str = set_codename(
            node_location,
            node_type,
            node_id
        )

        exists = await self.nodes_collection.find_one({"node_codename": node_codename})
        if exists:
            raise HTTPException(409, "Node with this codename already exists.")

        now = set_default_timezone()
        doc = node_data.model_dump(exclude_none=True)
        doc.update({
            "node_codename": node_codename,
            "description": node_data.description or None,
            "created_at": now,
            "latest_updated": now,
            "firmware_url": None,
            "firmware_version": None,
        })
        result = await self.nodes_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return NodeModel(**doc)
    
    async def get_node_by_codename(
        self,
        node_codename: str
    ) -> Optional[NodeModel]:
        doc = await self.nodes_collection.find_one(
            {"node_codename": node_codename}
        )
        return NodeModel(**doc) if doc else None
    
    async def update_firmware(
        self,
        node_codename: str,
        firmware_url: str,
        firmware_version: str
    ) -> NodeModel:
        """
        Update the firmware URL and version for a specific node.
            Method: PUT (updating existing document)
        """
        now = set_default_timezone()
        result = await self.nodes_collection.find_one_and_update(
            {"node_codename": node_codename},
            {"$set": {
                "firmware_url": firmware_url,
                "firmware_version": firmware_version,
                "latest_updated": now
            }},
            return_document=True
        )
        if not result:
            raise HTTPException(404, "Node not found.")
        return NodeModel(**result)
    
    async def delete_node(self, node_codename: str, firmware_version: Optional[str] = None) -> int:
        if firmware_version:
            result = await self.nodes_collection.delete_one({
                "node_codename": node_codename,
                "firmware_version": firmware_version
            })
        else:
            result = await self.nodes_collection.delete_one({"node_codename": node_codename})
        return result.deleted_count
    
    async def get_all_nodes(self, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[NodeModel]:
        cursor = self.nodes_collection.find(filters).sort("node_location", ASCENDING).skip(skip).limit(limit)
        nodes = await cursor.to_list(length=limit)
        return [NodeModel(**node) for node in nodes]
    
    async def count_nodes(self, filters: Dict[str, Any]) -> int:
        return await self.nodes_collection.count_documents(filters)
    
    async def get_filter_options(self) -> BaseFilterOptions:
        pipeline = [
            {"$group": {
                "_id": None,
                "node_location": {"$addToSet": "$node_location"},
                "node_type": {"$addToSet": "$node_type"}
            }},
            {"$project": {
                "_id": 0,
                "node_location": 1,
                "node_type": 1,
            }}
        ]
        result = await self.nodes_collection.aggregate(pipeline).to_list(length=1)
        return result[0] if result else {"node_location": [], "node_type": []}