from fastapi import Depends
from pymongo import ASCENDING, DESCENDING
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection
)

from enums.log import LogStatus
from models.node import NodeModel
from schemas.node import NodeCreateSchema
from schemas.common import BaseFilterOptions
from cores.dependencies import (
    get_db_connection,
    get_nodes_collection
)
from utils.datetime import get_current_datetime
from utils.validator import set_codename
from utils.logger import logger


class NodeRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        nodes_collection: AsyncIOMotorCollection = Depends(get_nodes_collection)
    ):
        self.db = db
        self.nodes_collection = nodes_collection

    async def add_new_node(self, node_data: NodeCreateSchema) -> Optional[NodeModel]:
        node_codename = set_codename(node_data.node_location, node_data.node_type, node_data.node_id)
        
        logger.db_info(f"Repository: Adding new node with codename '{node_codename}'")
        
        node_exist = await self.nodes_collection.find_one({"node_codename": node_codename})

        if node_exist:
            logger.db_warning(f"Repository: Node '{node_codename}' already exists")
            return None

        now = get_current_datetime()
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

        logger.db_info(f"Repository: Node '{node_codename}' added with ID: {result.inserted_id}")
        return NodeModel(**doc)

    async def upsert_firmware(
        self,
        node_codename: str,
        firmware_url: str,
        firmware_version: str
    ) -> Optional[NodeModel]:
        logger.db_info(f"Repository: Upserting firmware '{firmware_version}' for node '{node_codename}'")
        
        node = await self.nodes_collection.find_one({"node_codename": node_codename})
        now = get_current_datetime()

        # Check if this firmware version already exists for a specific node
        version_exist = await self.nodes_collection.find_one({
            "node_codename": node_codename,
            "firmware_version": firmware_version
        })

        if version_exist:
            logger.db_warning(f"Repository: Firmware version '{firmware_version}' already exists for node '{node_codename}'")
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

            logger.db_info(f"Repository: Updated existing node '{node_codename}' with first firmware version '{firmware_version}'")
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

            logger.db_info(f"Repository: Created new firmware version '{firmware_version}' for node '{node_codename}' with ID: {result.inserted_id}")
            return NodeModel(**new_doc) if new_doc else None

    async def update_description(
        self,
        node_codename: str,
        description: str,
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        logger.db_info(f"Repository: Updating description for node '{node_codename}' - Version: {firmware_version}")
        
        now = get_current_datetime()
        filter_query = {"node_codename": node_codename}
        if firmware_version:
            filter_query["firmware_version"] = firmware_version
            result = await self.nodes_collection.find_one_and_update(
                filter_query,
                {"$set": {"description": description, "latest_updated": now}},
                return_document=True
            )
            if not result:
                logger.db_warning(f"Repository: No node found for update - Codename: '{node_codename}', Version: '{firmware_version}'")
                return None

            logger.db_info(f"Repository: Description updated for node '{node_codename}' version '{firmware_version}'")
            return NodeModel(**result)
        else:
            update_result = await self.nodes_collection.update_many(
                filter_query,
                {"$set": {"description": description, "latest_updated": now}}
            )
            if update_result.modified_count == 0:
                logger.db_warning(f"Repository: No nodes updated for codename '{node_codename}'")
                return None

            # Optionally, return the first updated node
            doc = await self.nodes_collection.find_one(filter_query)
            logger.db_info(f"Repository: Description updated for {update_result.modified_count} node(s) with codename '{node_codename}'")
            return NodeModel(**doc) if doc else None

    async def delete_node(self, node_codename: str, firmware_version: Optional[str]) -> int:
        logger.db_info(f"Repository: Deleting node '{node_codename}' - Version: {firmware_version}")
        
        if firmware_version:
            result = await self.nodes_collection.delete_one({
                "node_codename": node_codename,
                "firmware_version": firmware_version
            })
            logger.db_info(f"Repository: Deleted {result.deleted_count} node(s) for '{node_codename}' version '{firmware_version}'")
        else:
            result = await self.nodes_collection.delete_many({"node_codename": node_codename})
            logger.db_info(f"Repository: Deleted {result.deleted_count} node(s) for '{node_codename}' (all versions)")

        return result.deleted_count

    async def get_all_nodes(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 10
    ) -> List[NodeModel]:
        logger.db_info(f"Repository: Retrieving nodes - Skip: {skip}, Limit: {limit}, Filters: {filters}")

        try:
            # Use aggregation pipeline to get the latest version of each node
            pipeline = [
                # Match documents based on filters
                {"$match": filters or {}},
                # Sort by firmware_version in descending order within each node_codename group
                {"$sort": {"node_codename": 1, "firmware_version": DESCENDING}},
                # Group by node_codename and keep the first document (latest version)
                {"$group": {
                    "_id": "$node_codename",
                    "doc": {"$first": "$$ROOT"}
                }},
                # Replace the root with the document from the group stage
                {"$replaceRoot": {"newRoot": "$doc"}},
                # Sort by created_at for consistent ordering
                {"$sort": {"node_codename": ASCENDING}},
                # Apply pagination
                {"$skip": skip},
                {"$limit": limit}
            ]
            
            nodes = await self.nodes_collection.aggregate(pipeline).to_list(length=limit)
            logger.db_info(f"Repository: Retrieved {len(nodes)} unique nodes (latest versions) from database")
            return [NodeModel(**node) for node in nodes]
        except Exception as e:
            logger.db_error("Repository: Failed to retrieve nodes", e)
            return []

    async def get_detail_node(
        self,
        node_codename: str,
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        """
        Get detailed information of a node by its codename and firmware version.
        
            - If firmware_version is None, it will return the latest firmware version for that node_codename.
            - If firmware_version is provided, it will return the specific version.
            - If no node is found, it returns None.
        """
        logger.db_info(f"Repository: Getting node details - Codename: '{node_codename}', Version: {firmware_version}")
        
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

        if doc:
            logger.db_info(f"Repository: Node details found for '{node_codename}'")
        else:
            logger.db_warning(f"Repository: No node details found for '{node_codename}' with version '{firmware_version}'")
            
        return NodeModel(**doc) if doc else None

    async def get_node_by_codename(self, node_codename: str) -> bool:
        logger.db_info(f"Repository: Checking if node '{node_codename}' exists")
        doc = await self.nodes_collection.find_one({"node_codename": node_codename})
        exists = True if doc else False
        logger.db_info(f"Repository: Node '{node_codename}' exists: {exists}")
        return exists

    async def get_firmware_versions(self, node_codename: str) -> Optional[List[str]]:
        logger.db_info(f"Repository: Getting firmware versions for node '{node_codename}'")
        
        docs = await (
            self.nodes_collection
            .find({"node_codename": node_codename})
            .sort("firmware_version", DESCENDING)
            .to_list(length=100)
        )

        versions = [doc["firmware_version"] for doc in docs if doc.get("firmware_version")]
        logger.db_info(f"Repository: Found {len(versions)} firmware versions for node '{node_codename}'")
        return versions

    async def count_nodes(self, filters: Dict[str, Any]) -> int:
        logger.db_info(f"Repository: Counting unique nodes with filters: {filters}")
        try:
            # Use aggregation to count unique node_codenames that match the filters
            pipeline = [
                {"$match": filters or {}},
                {"$group": {
                    "_id": "$node_codename"
                }},
                {"$count": "total"}
            ]
            
            result = await self.nodes_collection.aggregate(pipeline).to_list(length=1)
            count = result[0]["total"] if result else 0
            
            logger.db_info(f"Repository: Total unique nodes count: {count}")
            return count
        except Exception as e:
            logger.db_error("Repository: Failed to count unique nodes", e)
            return 0

    async def get_filter_options(self) -> BaseFilterOptions:
        logger.db_info("Repository: Getting filter options")
        try:
            pipeline = [
                {"$group": {
                    "_id": None,
                    "node_location": {"$addToSet": "$node_location"},
                    "node_type": {"$addToSet": "$node_type"}
                }},
                {"$project": {
                    "_id": 0,
                    "node_location": 1,
                    "node_type": 1
                }}
            ]

            result = await self.nodes_collection.aggregate(pipeline).to_list(length=1)

            if result:
                filter_options = BaseFilterOptions(
                    node_locations=result[0].get("node_location", []),
                    node_types=result[0].get("node_type", [])
                )
            else:
                filter_options = BaseFilterOptions(
                    node_locations=[],
                    node_types=[]
                )
            
            logger.db_info("Repository: Filter options retrieved successfully")
            return filter_options
        except Exception as e:
            logger.db_error("Repository: Failed to get filter options", e)
            return BaseFilterOptions(
                node_locations=[],
                node_types=[]
            )