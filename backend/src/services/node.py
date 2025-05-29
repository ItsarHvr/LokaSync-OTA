from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional, List

from repositories.node import NodeRepository
from schemas.node import NodeCreateSchema, NodeModifyVersionSchema
from models.node import NodeModel

class NodeService:
    def __init__(self, node_repository: NodeRepository = Depends()):
        self.node_repository = node_repository

    async def add_node_location(self, data: NodeCreateSchema) -> NodeModel:
        added = await self.node_repository.add_node_location(data)

        if not added:
            raise HTTPException(409, "Node already exists.")
        
        return added

    async def upsert_firmware(self, node_codename: str, data: NodeModifyVersionSchema) -> NodeModel:
        # Validate that the firmware URL and version are provided
        firmware_url = data.firmware_url
        firmware_version = data.firmware_version
        if not firmware_url or not firmware_version:
            raise HTTPException(400, "Firmware URL and version must be provided.")

        # Upsert the firmware version for the node
        node = await self.node_repository.upsert_firmware(
            node_codename=node_codename,
            firmware_url=firmware_url,
            firmware_version=firmware_version
        )

        # Check if the node was successfully created or updated
        if not node:
            raise HTTPException(409, "Firmware version already exists for this node or failed to upsert.")

        return node

    async def update_description(
        self,
        node_codename: str,
        description: Optional[str],
        firmware_version: Optional[str]
    ) -> NodeModel:
        updated = await self.node_repository.update_description(
            node_codename,
            description,
            firmware_version
        )
        if not updated:
            raise HTTPException(404, "Node not found or firmware version mismatch.")
        
        return updated

    async def get_node(self, node_codename: str) -> NodeModel:
        node = await self.node_repository.get_node_by_codename(node_codename)
        if not node:
            raise HTTPException(404, "Node not found.")

        return node

    async def delete_node(self, node_codename: str, firmware_version: Optional[str] = None) -> None:
        deleted = await self.node_repository.delete_node(node_codename, firmware_version)
        if not deleted:
            raise HTTPException(404, "Node not found or firmware version mismatch.")

    async def get_all_nodes(self, filters: Dict[str, Any], skip: int, limit: int):
        return await self.node_repository.get_all_nodes(filters, skip, limit)

    async def get_detail_node(self, node_codename: str, firmware_version: str) -> NodeModel:
        node = await self.node_repository.get_detail_node(node_codename, firmware_version)
        if not node:
            raise HTTPException(404, "Node not found or firmware version mismatch.")

        return node

    async def get_firmware_versions(self, node_codename: str) -> Optional[List[str]]:
        return await self.node_repository.get_firmware_versions(node_codename)

    async def count_nodes(self, filters: Dict[str, Any]) -> int:
        return await self.node_repository.count_nodes(filters)

    async def get_filter_options(self):
        return await self.node_repository.get_filter_options()