import os
from fastapi import Depends, UploadFile
from fastapi.exceptions import HTTPException
from typing import Optional
from datetime import datetime, timezone
from math import ceil

from cores.config import env
from cores.dependencies import get_current_user
from externals.gdrive.client import SERVICE_ACCOUNT_FILE, SCOPES
from externals.gdrive.uploader import upload_file
from repositories.firmware import FirmwareRepository
from schemas.firmware import (
    InputFirmware,
    UpdateFirmware,
    UpdateFirmwareDescription,
    OutputFirmwarePagination,
    OuputFirmwareByNodeName
)


class ServiceFirmware:
    def __init__(self, firmware_repository: FirmwareRepository = Depends()):
        self.firmware_repository = firmware_repository
        self.gdrive_folder_id = env.GOOGLE_DRIVE_FOLDER_ID
        # print("DEBUG folder_id:", repr(self.gdrive_folder_id))

    async def get_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        user: dict = Depends(get_current_user)
    ) -> OutputFirmwarePagination:
        try:
            # 1. Check user authentication
            if not user:
                raise HTTPException(status_code=401, detail="Unauthorized access")
            
            # 2. Data firmware
            list_firmware = await self.firmware_repository.get_list_firmware(
                page=page,
                page_size=page_size,
                node_id=node_id,
                node_location=node_location,
            )

            # 3. Total data
            total_data = await self.firmware_repository.count_list_firmware(
                node_id=node_id,
                node_location=node_location,
            )

            # 4. Total page
            total_page = ceil(total_data / page_size) if total_data else 1

            # 5. Get filter options
            filter_options = await self.firmware_repository.get_filter_options()

            # 6. Return response
            return OutputFirmwarePagination(
                page=page,
                page_size=page_size,
                total_data=total_data,
                total_page=total_page,
                filter_options=filter_options,
                firmware_data=list_firmware,
            )
        except Exception as e:
            return HTTPException(status_code=500, detail=f"Failed to get firmware list")

    async def get_list_firmware_version(
        self,
        node_name: str,
        user: dict = Depends(get_current_user)
    ) -> OuputFirmwareByNodeName:
        """Return:
        - Only return the firmware version list associated with the node name.
        """
        try:
            # 1. Check user authentication
            if not user:
                raise HTTPException(status_code=401, detail="Unauthorized access") 
            
            # 2. Get list firmware version by node name
            list_firmware_version = await self.firmware_repository.get_list_firmware_version(
                node_name
            )

            return OuputFirmwareByNodeName(list_firmware_version=list_firmware_version)
        except Exception as e:
            return HTTPException(status_code=500, detail="Failed to get firmware list by node name")

    async def add_new_node(
        self,
        input_firmware: InputFirmware,
        user: dict = Depends(get_current_user)
    ):
        # Stage 1: Always check user authentication
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized access")
        
        # Stage 2: Save firmware file in local folder
        filename = input_firmware.firmware_file.filename
        save_path = f"tmp/{filename}"
        
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
            
        try:
            with open(save_path, "wb+") as f:
                content = await input_firmware.firmware_file.read()
                f.write(content)
        except Exception as e:
            return HTTPException(status_code=500, detail="Failed to save firmware file in local folder")
        
        # Stage 3: Upload firmware file to Google drive
        try:
            firmware_url = upload_file(save_path, filename, self.gdrive_folder_id)
        except Exception as e:
            return HTTPException(status_code=500, detail="Failed to upload firmware file to Google Drive")
        
        # Stage 4: Prepare firmware data
        firmware_data = {
            "firmware_description": input_firmware.firmware_description,
            "firmware_version": input_firmware.firmware_version,
            "firmware_url": firmware_url,
            "node_id": input_firmware.node_id,
            "node_location": input_firmware.node_location,
            "node_name": input_firmware.node_name,
            "latest_updated": datetime.now(timezone.tzname(env.TIMEZONE))
        }

        # Stage 5: Insert firmware data to MongoDB
        try:
            await self.firmware_repository.add_new_node(firmware_data, user)
        except Exception as e:
            return HTTPException(f"Failed to insert firmware data")
        
        # #Publish ke MQTT
        # try:
        #     topic = "LokaSync/CloudOTA/Firmware"
        #     payload = json.dumps({
        #         "node_name":node_name,
        #         "firmware_version": firmware_version,
        #         "url": firmware_url
        #     })
        #     publish.single(topic, payload, hostname=MQTT_ADDRESS)
        # except Exception as e:
        #     raise Exception(f"Gagal Mengirim ke MQTT: {str(e)}")
        
    async def update_firmware_version(
        self,
        node_name: str,
        update_firmware: UpdateFirmware,
        user: dict = Depends(get_current_user)
    ):
        # Stage 1: Always check user authentication
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized access")
        
        # Stage 2: Save firmware file in local folder
        filename = update_firmware.firmware_file.filename
        save_path = f"tmp/{filename}"
        
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        
        try:
            with open(save_path, "wb+") as f:
                content = await update_firmware.firmware_file.read()
                f.write(content)
        except Exception as e:
            return HTTPException(f"Failed to save firmware file in local folder")
        
        # Stage 3: Upload firmware file to Google drive
        try:
            firmware_url = upload_file(save_path, filename, self.gdrive_folder_id)
        except Exception as e:
            return HTTPException(f"Failed to upload firmware file to Google Drive")
        
        # Stage 4: Update firmware version in MongoDB
        try:
            return await self.firmware_repository.update_firmware_version(
                node_name,
                {
                    "firmware_description": getattr(update_firmware, "firmware_description", ""),
                    "firmware_version": update_firmware.firmware_version,
                    "firmware_url": firmware_url,
                }
            )
        except Exception as e:
            return HTTPException("Failed to update firmware version")
        
        # try:
        #     topic = "LokaSync/CloudOTA/Firmware"
        #     payload = json.dumps({
        #         "node_name": node_name,
        #         "url": firmware_url,
        #         "firmware_version": form.firmware_version
        #     })
        #     publish.single(topic, payload, hostname=MQTT_ADDRESS)
        # except Exception as e:
        #     raise Exception(f"Gagal Mengirim ke MQTT: {str(e)}")
        
        # return {"message": "Update firmware successfully."}
    
    async def update_firmware_description(
        self,
        node_name: str,
        firmware_version: str,
        update_firmware: UpdateFirmwareDescription,
        user: dict = Depends(get_current_user)
    ):
        try:
            # Stage 1: Always check user authentication
            if not user:
                raise HTTPException(status_code=401, detail="Unauthorized access")
            
            # Stage 2: Update firmware description in MongoDB
            return await self.firmware_repository.update_firmware_description(
                node_name,
                firmware_version,
                { "firmware_description": update_firmware.firmware_description }
            )
        except Exception as e:
            return HTTPException(status_code=500, detail="Failed to update firmware description")

    async def delete_firmware_version(
        self,
        node_name: str,
        firmware_version: str,
        user: dict = Depends(get_current_user)
    ):
        try:
            # Stage 1: Always check user authentication
            if not user:
                raise HTTPException(status_code=401, detail="Unauthorized access")

            # Stage 2: Delete specific firmware version
            return await self.firmware_repository.delete_firmware_verison(
                node_name,
                firmware_version
            )
        except Exception as e:
            return HTTPException(status_code=500, detail="Failed to delete firmware by version")

    async def delete_all_version(
        self,
        node_name: str,
        user: dict= Depends(get_current_user)
    ):
        try:
            # Stage 1: Always check user authentication
            if not user:
                raise HTTPException(status_code=401, detail="Unauthorized access")

            # Stage 2: Delete all firmware versions by node name
            return await self.firmware_repository.delete_all_version(node_name)
        except Exception as e:
            return HTTPException(status_code=500, detail="Failed to delete all firmwares by node name")