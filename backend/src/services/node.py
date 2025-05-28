from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional

from repositories.node import NodeRepository
from schemas.node import NodeCreateSchema, NodeModifyVersionSchema
from models.node import NodeModel
from utils.datetime import set_default_timezone
from externals.gdrive.uploader import upload_file

class NodeService:
    def __init__(self, node_repository: NodeRepository = Depends()):
        self.node_repository = node_repository

    async def add_node_location(self, data: NodeCreateSchema) -> NodeModel:
        return await self.node_repository.add_node_location(data)

    async def add_first_version(self, node_codename: str, data: NodeModifyVersionSchema) -> NodeModel:
        # Only allow update of firmware_version and firmware_url
        firmware_url = data.firmware_url

        if data.firmware_file:
            firmware_url = upload_file(await data.firmware_file.read(), data.firmware_file.filename)
        if not firmware_url:
            raise HTTPException(400, "Firmware URL or file must be provided.")
        return await self.node_repository.update_firmware(
            node_codename=node_codename,
            firmware_url=firmware_url,
            firmware_version=data.firmware_version
        )
    
    async def add_new_version(self, node_codename: str, data: NodeModifyVersionSchema) -> NodeModel:
        node = await self.node_repository.get_node_by_codename(node_codename)
        if not node:
            raise HTTPException(404, "Node not found.")
        firmware_url = data.firmware_url
        if data.firmware_file:
            firmware_url = upload_file(await data.firmware_file.read(), data.firmware_file.filename)
        if not firmware_url:
            raise HTTPException(400, "Firmware URL or file must be provided.")
        return await self.node_repository.update_firmware(
            node_codename=node_codename,
            firmware_url=firmware_url,
            firmware_version=data.firmware_version
        )

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

    async def count_nodes(self, filters: Dict[str, Any]) -> int:
        return await self.node_repository.count_nodes(filters)

    async def get_filter_options(self):
        return await self.node_repository.get_filter_options()