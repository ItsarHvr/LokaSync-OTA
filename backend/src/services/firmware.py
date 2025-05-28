import asyncio
import os
from fastapi import Depends, HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from math import ceil

from cores.config import env
from cores.dependencies import get_current_user
from externals.gdrive.uploader import upload_file
from repositories.firmware import FirmwareRepository
from schemas.firmware import (
    InputNewNode,
    UpdateFirmwareVersion,
    UpdateFirmwareDescription,
    OutputFirmwarePagination,
    OuputFirmwareByNodeName
)


class ServiceFirmware:
    def __init__(self, firmware_repository: FirmwareRepository = Depends()):
        self.firmware_repository = firmware_repository
        self.gdrive_folder_id = env.GOOGLE_DRIVE_FOLDER_ID

    async def get_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        user: Dict[str, Any] = Depends(get_current_user)
    ) -> OutputFirmwarePagination:
        """Get paginated firmware list with filters."""
        try:
            # Get firmware data and total count concurrently
            list_firmware, total_data, filter_options = await asyncio.gather(
                self.firmware_repository.get_list_firmware(page, page_size, node_id, node_location),
                self.firmware_repository.count_list_firmware(node_id, node_location),
                self.firmware_repository.get_filter_options()
            )

            total_page = ceil(total_data / page_size) if total_data else 1

            return OutputFirmwarePagination(
                page=page,
                page_size=page_size,
                total_data=total_data,
                total_page=total_page,
                filter_options=filter_options,
                firmware_data=list_firmware,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to get firmware list")

    async def get_list_firmware_version(
        self,
        node_name: str,
        user: Dict[str, Any] = Depends(get_current_user)
    ) -> OuputFirmwareByNodeName:
        """Get firmware version list by node name."""
        try:
            list_firmware_version = await self.firmware_repository.get_list_firmware_version(node_name)
            # Extract just the version strings
            versions = [fw.firmware_version for fw in list_firmware_version]
            
            return OuputFirmwareByNodeName(list_firmware_version=versions)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to get firmware list by node name")

    async def add_new_node(
        self,
        input_firmware: InputNewNode,
        user: Dict[str, Any] = Depends(get_current_user)
    ):
        """Add new firmware node."""
        try:
            # Save and upload firmware file
            firmware_url = await self._process_firmware_file(input_firmware.firmware_file)
            
            # Prepare firmware data
            firmware_data = self._build_firmware_data(input_firmware, firmware_url, user)
            
            # Insert to database
            await self.firmware_repository.add_new_node(firmware_data)
            
            return {"message": "Firmware added successfully", "status_code": 201}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to add new firmware")

    async def update_firmware_version(
        self,
        node_name: str,
        update_firmware: UpdateFirmwareVersion,
        user: Dict[str, Any] = Depends(get_current_user)
    ):
        """Update firmware version for a node."""
        try:
            # Process firmware file
            firmware_url = await self._process_firmware_file(update_firmware.firmware_file)
            
            # Update firmware
            update_data = {
                "firmware_description": getattr(update_firmware, "firmware_description", ""),
                "firmware_version": update_firmware.firmware_version,
                "firmware_url": firmware_url,
            }
            
            result = await self.firmware_repository.update_firmware_version(node_name, update_data)
            if not result:
                raise HTTPException(status_code=404, detail="Node not found")
            
            return {"message": "Firmware version updated successfully", "status_code": 200}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to update firmware version")

    async def update_firmware_description(
        self,
        node_name: str,
        firmware_version: str,
        update_firmware: UpdateFirmwareDescription,
        user: Dict[str, Any] = Depends(get_current_user)
    ):
        """Update firmware description."""
        try:
            success = await self.firmware_repository.update_firmware_description(
                node_name,
                firmware_version,
                {"firmware_description": update_firmware.firmware_description}
            )
            
            if not success:
                raise HTTPException(status_code=404, detail="Firmware version not found")
            
            return {"message": "Firmware description updated successfully", "status_code": 200}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to update firmware description")

    async def delete_firmware_version(
        self,
        node_name: str,
        firmware_version: str,
        user: Dict[str, Any] = Depends(get_current_user)
    ):
        """Delete specific firmware version."""
        try:
            result = await self.firmware_repository.delete_firmware_version(node_name, firmware_version)
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Firmware version not found")
            
            return {"message": "Firmware version deleted successfully", "status_code": 200}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to delete firmware version")

    async def delete_all_version(
        self,
        node_name: str,
        user: Dict[str, Any] = Depends(get_current_user)
    ):
        """Delete all firmware versions for a node."""
        try:
            result = await self.firmware_repository.delete_all_version(node_name)
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="No firmware found for this node")
            
            return {"message": f"All firmware versions for {node_name} deleted successfully", "status_code": 200}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to delete firmware versions")

    # Helper methods
    async def _process_firmware_file(self, firmware_file) -> str:
        """Process and upload firmware file."""
        if not firmware_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        filename = firmware_file.filename
        save_path = f"tmp/{filename}"
        
        # Create temp directory if it doesn't exist
        os.makedirs("tmp", exist_ok=True)
        
        try:
            # Save file temporarily
            with open(save_path, "wb") as f:
                content = await firmware_file.read()
                f.write(content)
            
            # Upload to Google Drive
            firmware_url = upload_file(save_path, filename, self.gdrive_folder_id)
            
            # Clean up temp file
            try:
                os.remove(save_path)
            except OSError:
                pass  # File might already be deleted
                
            return firmware_url
            
        except Exception as e:
            # Clean up temp file on error
            try:
                os.remove(save_path)
            except OSError:
                pass
            raise HTTPException(status_code=500, detail=f"Failed to process firmware file: {str(e)}")

    def _build_firmware_data(self, input_firmware: InputNewNode, firmware_url: str, user: Dict[str, Any]) -> dict:
        """Build firmware data dictionary."""
        return {
            "firmware_description": input_firmware.firmware_description or "",
            "firmware_version": input_firmware.firmware_version,
            "firmware_url": firmware_url,
            "node_id": input_firmware.node_id,
            "node_location": input_firmware.node_location.value if hasattr(input_firmware.node_location, 'value') else input_firmware.node_location,
            "node_name": getattr(input_firmware, 'node_name', f"{input_firmware.node_location.lower()}-node{input_firmware.node_id}"),
            "created_by": user.get("uid", "unknown"),
            "created_by_email": user.get("email", "unknown"),
            "latest_updated": datetime.now(timezone.tzname(env.TIMEZONE))
        }