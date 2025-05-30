from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import DESCENDING
from typing import List, Dict, Any, Optional

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

    async def add_node_location(self, node_data: NodeCreateSchema) -> Optional[NodeModel]:
        node_codename = set_codename(node_data.node_location, node_data.node_type, node_data.node_id)
        node_exist = await self.nodes_collection.find_one({"node_codename": node_codename})

        if node_exist:
            return None

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

    async def upsert_firmware(
        self,
        node_codename: str,
        firmware_url: str,
        firmware_version: str
    ) -> Optional[NodeModel]:
        node = await self.nodes_collection.find_one({"node_codename": node_codename})
        now = set_default_timezone()

        # Check if this firmware version already exists for a specific node
        version_exist = await self.nodes_collection.find_one({
            "node_codename": node_codename,
            "firmware_version": firmware_version
        })

        if version_exist:
            return None

        # If node exists and has no firmware version, update with the first firmware version
        if node and (not node.get("firmware_url") and not node.get("firmware_version")):
            # Update existing node with first firmware
            result = await self.nodes_collection.find_one_and_update(
                {"node_codename": node_codename},
                {"$set": {
                    "firmware_url": firmware_url,
                    "firmware_version": firmware_version,
                    "latest_updated": now
                }},
                return_document=True
            )

            return NodeModel(**result) if result else None
        # If node exists and has firmware version, create a new firmware version
        else:
            # Create new node document with same codename but new firmware
            new_doc = node.copy() if node else {}
            new_doc.update({
                "firmware_url": firmware_url,
                "firmware_version": firmware_version,
                "latest_updated": now,
                "created_at": now,
            })

            new_doc.pop("_id", None)
            result = await self.nodes_collection.insert_one(new_doc)
            new_doc["_id"] = result.inserted_id

            return NodeModel(**new_doc) if new_doc else None

    async def update_description(
        self,
        node_codename: str,
        description: str,
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        now = set_default_timezone()
        filter_query = {"node_codename": node_codename}
        if firmware_version:
            filter_query["firmware_version"] = firmware_version
            result = await self.nodes_collection.find_one_and_update(
                filter_query,
                {"$set": {"description": description, "latest_updated": now}},
                return_document=True
            )
            if not result:
                return None

            return NodeModel(**result)
        else:
            update_result = await self.nodes_collection.update_many(
                filter_query,
                {"$set": {"description": description, "latest_updated": now}}
            )
            if update_result.modified_count == 0:
                return None

            # Optionally, return the first updated node
            doc = await self.nodes_collection.find_one(filter_query)
            return NodeModel(**doc) if doc else None

    async def delete_node(self, node_codename: str, firmware_version: Optional[str]) -> int:
        if firmware_version:
            result = await self.nodes_collection.delete_one({
                "node_codename": node_codename,
                "firmware_version": firmware_version
            })
        else:
            result = await self.nodes_collection.delete_many({"node_codename": node_codename})

        return result.deleted_count

    async def get_all_nodes(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 10
    ) -> List[NodeModel]:
        """
        Get all nodes with latest firmware version based on filters, skip, and limit.
        This method aggregates nodes to get the latest firmware version for each node codename.
        """
        pipeline = [
            {"$match": filters},
            {"$sort": {"firmware_version": DESCENDING}},
            {"$group": {
                "_id": "$node_codename",
                "doc": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$doc"}},
            {"$sort": {"node_location": 1, "node_id": 1}},
            {"$skip": skip},
            {"$limit": limit}
        ]

        nodes = await self.nodes_collection.aggregate(pipeline).to_list(length=limit)
        return [NodeModel(**node) for node in nodes]

    async def get_detail_node(
        self,
        node_codename: str,
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        """
        Get detailed information of a node by its codename and firmware version.
        
            - If firmware_version is None, it will return the latest firmware version for that node_codename.
            - If firmware_version is provided, it will return the specific version.
            - If no node is found, it returns empty list.
        """
        query = {"node_codename": node_codename}
        if firmware_version:
            # If firmware_version is provided, filter by it
            query["firmware_version"] = firmware_version
            doc = await self.nodes_collection.find_one(query)
        else:
            # Get the latest firmware_version for this node_codename
            doc = await (
                self.nodes_collection
                .find(query)
                .sort("firmware_version", DESCENDING)
                .limit(1)
                .to_list(length=1)
            )
            doc = doc[0] if doc else None
        
        return NodeModel(**doc) if doc else None

    async def get_node_by_codename(self, node_codename: str) -> bool:
        doc = await self.nodes_collection.find_one({"node_codename": node_codename})
        return True if doc else False

    async def get_firmware_versions(self, node_codename: str) -> Optional[List[str]]:
        docs = await (
            self.nodes_collection
            .find({"node_codename": node_codename})
            .sort("firmware_version", DESCENDING)
            .to_list(length=100)
        )

        return [doc["firmware_version"] for doc in docs if doc.get("firmware_version")]

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
        if result:
            return BaseFilterOptions(
                node_locations=result[0].get("node_location", []),
                node_types=result[0].get("node_type", [])
            )

        # Return empty lists if not have result
        return BaseFilterOptions(node_locations=[], node_types=[])