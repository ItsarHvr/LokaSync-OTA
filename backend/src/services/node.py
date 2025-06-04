from io import BytesIO
from fastapi import Depends, HTTPException, UploadFile, requests
from typing import Dict, Any, List, Optional, Tuple

from repositories.node import NodeRepository
from models.node import NodeModel
from schemas.node import NodeCreateSchema, NodeModifyVersionSchema
from schemas.common import BaseFilterOptions
from utils.logger import logger
from cores.config import env
from externals.gdrive.download import download_firmware_from_gdrive


class NodeService:
    def __init__(self, nodes_repository: NodeRepository = Depends()):
        self.nodes_repository = nodes_repository
    
    async def add_new_node(self, data: NodeCreateSchema) -> Optional[NodeModel]:
        logger.api_info(f"Service: Adding new node with data", data.model_dump())
        added = await self.nodes_repository.add_new_node(data)

        # Business Logic: Validate if node already exists
        if not added:
            logger.api_error("Service: Node already exists")
            raise HTTPException(409, "Node already exists.")

        logger.api_info(f"Service: Node added successfully - Codename: {added.node_codename}")
        return added

    async def upsert_firmware(
        self,
        node_codename: str,
        data: NodeModifyVersionSchema,
    ) -> Optional[NodeModel]:
        """
        Upsert firmware with comprehensive business logic validation.
        Handles both file upload and URL scenarios.
        """
        # Extract data from schema
        firmware_url = data.firmware_url
        firmware_version = data.firmware_version
        firmware_file = data.firmware_file

        logger.api_info(f"Service: Upserting firmware for node '{node_codename}' - Version: '{firmware_version}'")

        # Business Logic: Validate that either file or URL is provided
        if not firmware_file and not firmware_url:
            logger.api_error("Service: Either firmware file or URL must be provided")
            raise HTTPException(400, "Either firmware file or URL must be provided.") 

        # Business Logic: Validate file type if file is provided
        if firmware_file and not firmware_file.filename.endswith('.bin'):
            logger.api_error("Service: Invalid file type provided")
            raise HTTPException(400, "Only .bin files are allowed.")
        
        # Business Logic: Validate firmware file size if file is provided
        if firmware_file:
            # Get file size
            firmware_file.file.seek(0, 2)  # Seek to end
            file_size = firmware_file.file.tell()
            firmware_file.file.seek(0)  # Reset to beginning
            
            max_size = env.GOOGLE_DRIVE_MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
            if file_size > max_size:
                logger.api_error(f"Service: File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)")
                raise HTTPException(400, f"File size exceeds maximum allowed size of {env.GOOGLE_DRIVE_MAX_FILE_SIZE_MB} MB.")
            
            logger.api_info(f"Service: File size validation passed - Size: {file_size} bytes")
        
        # Business Logic: Check if node exists
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")

        # Business Logic: Delegate to repository for the actual upsert
        upserted = await self.nodes_repository.upsert_firmware(
            node_codename=node_codename,
            firmware_version=firmware_version,
            firmware_url=firmware_url,
            firmware_file=firmware_file
        )

        if not upserted:
            logger.api_error(f"Service: Firmware version '{firmware_version}' already exists for node '{node_codename}'")
            raise HTTPException(409, "Firmware version already exists for this node.")

        logger.api_info(f"Service: Firmware upserted successfully for node '{node_codename}'")
        return upserted

    async def get_firmware_download(self, node_codename: str, firmware_version: str = None) -> Tuple[BytesIO, str]:
        """
        Get firmware file for download with business logic validation.
        """
        logger.api_info(f"Service: Getting firmware download for node '{node_codename}' version '{firmware_version}'")
        
        # Business Logic: Check if node exists
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")
        
        # Business Logic: Get firmware info
        firmware_info = await self.nodes_repository.get_firmware_download_info(node_codename, firmware_version)
        if not firmware_info:
            logger.api_error(f"Service: Firmware not found for node '{node_codename}' version '{firmware_version}'")
            raise HTTPException(404, "Firmware not found.")
        
        firmware_url = firmware_info['firmware_url']
        
        # Business Logic: Handle different URL types
        if 'drive.google.com' in firmware_url:
            # Extract file ID from Google Drive URL
            if 'id=' in firmware_url:
                file_id = firmware_url.split('id=')[1].split('&')[0]
            else:
                logger.api_error(f"Service: Invalid Google Drive URL format")
                raise HTTPException(400, "Invalid Google Drive URL format.")
            
            download_result = download_firmware_from_gdrive(file_id)
            if not download_result:
                logger.api_error(f"Service: Failed to download firmware from Google Drive")
                raise HTTPException(500, "Failed to download firmware from Google Drive.")
            
            file_content, filename, _ = download_result
            logger.api_info(f"Service: Successfully retrieved firmware from Google Drive: {filename}")
            return file_content, filename
        else:
            # Business Logic: Handle other URL types (future enhancement)
            logger.api_error(f"Service: Direct URL download not implemented yet")
            raise HTTPException(501, "Direct URL download not implemented yet.")

    async def update_description(
        self,
        node_codename: str,
        description: Optional[str],
        firmware_version: Optional[str]
    ) -> Optional[NodeModel]:
        logger.api_info(f"Service: Updating description for node '{node_codename}'")
        
        # Business Logic: Check if node exists
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
        logger.api_info(f"Service: Deleting node '{node_codename}' - Version: '{firmware_version}'")

        # Business Logic: Check if node exists
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: Node '{node_codename}' not found")
            raise HTTPException(404, "Node not found.")

        deleted_count = await self.nodes_repository.delete_node(node_codename, firmware_version)
        if deleted_count == 0:
            logger.api_error(f"Service: Firmware version not found for node '{node_codename}'")
            raise HTTPException(404, "Firmware version not found.")
        
        logger.api_info(f"Service: Node '{node_codename}' deleted successfully - {deleted_count} record(s) removed")

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
        logger.api_info(f"Service: Getting node details - Codename: '{node_codename}', Version: '{firmware_version}'")

        # Business Logic: Check if node exists
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
        
        # Business Logic: Check if node exists
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