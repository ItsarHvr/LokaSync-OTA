from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional, List

from repositories.node import NodeRepository
from schemas.common import BaseFilterOptions
from schemas.node import NodeCreateSchema, NodeModifyVersionSchema
from models.node import NodeModel


class NodeService:
    def __init__(self, nodes_repository: NodeRepository = Depends()):
        self.nodes_repository = nodes_repository

    async def add_node_location(self, data: NodeCreateSchema) -> Optional[NodeModel]:
        added = await self.nodes_repository.add_node_location(data)

        if not added:
            raise HTTPException(409, "Node already exists.")

        return added

    async def upsert_firmware(
        self,
        node_codename: str,
        data: NodeModifyVersionSchema
    ) -> Optional[NodeModel]:
        firmware_url = data.firmware_url
        firmware_version = data.firmware_version
        if not firmware_url and not firmware_version:
            raise HTTPException(400, "Firmware URL and version must be provided.")
        
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            raise HTTPException(404, "Node not found.")

        # Upsert the firmware version for the node
        upserted = await self.nodes_repository.upsert_firmware(
            node_codename=node_codename,
            firmware_url=firmware_url,
            firmware_version=firmware_version
        )

        # Check if the node was successfully created or updated
        if not upserted:
            raise HTTPException(409, "Firmware version already exists for this node.")

        return upserted

    async def update_description(
        self,
        node_codename: str,
        description: Optional[str],
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            raise HTTPException(404, "Node not found.")

        updated = await self.nodes_repository.update_description(
            node_codename,
            description,
            firmware_version
        )
        if not updated:
            raise HTTPException(404, "Firmware version not found.")
        
        return updated

    async def delete_node(
        self,
        node_codename: str,
        firmware_version: Optional[str]
    ) -> None:
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            raise HTTPException(404, "Node not found.")

        deleted = await self.nodes_repository.delete_node(node_codename, firmware_version)
        if not deleted:
            raise HTTPException(404, "Firmware version not found.")

    async def get_all_nodes(
        self,
        filters: Dict[str, Any],
        skip: int,
        limit: int
    ) -> List[NodeModel]:
        return await self.nodes_repository.get_all_nodes(filters, skip, limit)

    async def get_detail_node(
        self,
        node_codename: str,
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            raise HTTPException(404, "Node not found.")

        node = await self.nodes_repository.get_detail_node(node_codename, firmware_version)
        if not node:
            raise HTTPException(404, "Firmware version not found.")

        return node

    async def get_firmware_versions(self, node_codename: str) -> Optional[List[str]]:
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            raise HTTPException(404, "Node not found.")

        versions = await self.nodes_repository.get_firmware_versions(node_codename)
        return versions

    async def count_nodes(self, filters: Dict[str, Any]) -> int:
        return await self.nodes_repository.count_nodes(filters)

    async def get_filter_options(self) -> BaseFilterOptions:
        return await self.nodes_repository.get_filter_options()