from fastapi import Depends, HTTPException
from typing import Dict, Any, List, Optional

from repositories.node import NodeRepository
from models.node import NodeModel
from schemas.node import NodeCreateSchema, NodeModifyVersionSchema
from schemas.common import BaseFilterOptions
from utils.logger import logger


class NodeService:
    def __init__(self, nodes_repository: NodeRepository = Depends()):
        self.nodes_repository = nodes_repository

    async def add_new_node(self, data: NodeCreateSchema) -> Optional[NodeModel]:
        logger.api_info(f"Service: Adding new node with data", data.model_dump())
        added = await self.nodes_repository.add_new_node(data)

        if not added:
            logger.api_error("Service: Node already exists")
            raise HTTPException(409, "Node already exists.")

        logger.api_info(f"Service: Node added successfully - Codename: {added.node_codename}")
        return added

    async def upsert_firmware(
        self,
        node_codename: str,
        data: NodeModifyVersionSchema
    ) -> Optional[NodeModel]:
        firmware_url = data.firmware_url
        firmware_version = data.firmware_version
        
        logger.api_info(f"Service: Upserting firmware for node '{node_codename}' - Version: {firmware_version}")
        
        if not firmware_url and not firmware_version:
            logger.api_error("Service: Firmware URL and version must be provided")
            raise HTTPException(400, "Firmware URL and version must be provided.")
        
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")

        # Upsert the firmware version for the node
        upserted = await self.nodes_repository.upsert_firmware(
            node_codename=node_codename,
            firmware_url=firmware_url,
            firmware_version=firmware_version
        )

        # Check if the node was successfully created or updated
        if not upserted:
            logger.api_error(f"Service: Firmware version '{firmware_version}' already exists for node '{node_codename}'")
            raise HTTPException(409, "Firmware version already exists for this node.")

        logger.api_info(f"Service: Firmware upserted successfully for node '{node_codename}'")
        return upserted

    async def update_description(
        self,
        node_codename: str,
        description: Optional[str],
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        logger.api_info(f"Service: Updating description for node '{node_codename}'")
        
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")

        updated = await self.nodes_repository.update_description(
            node_codename,
            description,
            firmware_version
        )
        if not updated:
            logger.api_error(f"Service: Firmware version not found for node '{node_codename}'")
            raise HTTPException(404, "Firmware version not found.")
        
        logger.api_info(f"Service: Description updated for node '{node_codename}'")
        return updated

    async def delete_node(
        self,
        node_codename: str,
        firmware_version: Optional[str]
    ) -> None:
        logger.api_info(f"Service: Deleting node '{node_codename}' - Version: {firmware_version}")
        
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")

        deleted = await self.nodes_repository.delete_node(node_codename, firmware_version)
        if not deleted:
            logger.api_error(f"Service: Firmware version not found for node '{node_codename}'")
            raise HTTPException(404, "Firmware version not found.")
        
        logger.api_info(f"Service: Node '{node_codename}' deleted successfully - {deleted} record(s) removed")

    async def get_all_nodes(
        self,
        filters: Dict[str, Any],
        skip: int,
        limit: int
    ) -> List[NodeModel]:
        logger.api_info(f"Service: Retrieving nodes with filters: {filters}")
        nodes = await self.nodes_repository.get_all_nodes(filters, skip, limit)
        logger.api_info(f"Service: Retrieved {len(nodes)} nodes")
        return nodes

    async def get_detail_node(
        self,
        node_codename: str,
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        logger.api_info(f"Service: Getting node details - Codename: '{node_codename}', Version: {firmware_version}")
        
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")

        node = await self.nodes_repository.get_detail_node(node_codename, firmware_version)
        if not node:
            logger.api_error(f"Service: Specific firmware version not found for node '{node_codename}'")
            raise HTTPException(404, "Firmware version not found.")
        
        logger.api_info(f"Service: Node details retrieved for '{node_codename}'")
        return node

    async def get_firmware_versions(self, node_codename: str) -> Optional[List[str]]:
        logger.api_info(f"Service: Getting firmware versions for node '{node_codename}'")
        
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")

        versions = await self.nodes_repository.get_firmware_versions(node_codename)
        logger.api_info(f"Service: Found {len(versions) if versions else 0} firmware versions for node '{node_codename}'")
        return versions

    async def count_nodes(self, filters: Dict[str, Any]) -> int:
        logger.api_info(f"Service: Counting nodes with filters: {filters}")
        count = await self.nodes_repository.count_nodes(filters)
        logger.api_info(f"Service: Total nodes count: {count}")
        return count

    async def get_filter_options(self) -> BaseFilterOptions:
        logger.api_info("Service: Getting filter options")
        options = await self.nodes_repository.get_filter_options()
        logger.api_info("Service: Filter options retrieved")
        return options