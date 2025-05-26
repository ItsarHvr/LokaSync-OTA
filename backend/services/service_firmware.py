import os
import json
from dotenv import load_dotenv
import paho.mqtt.publish as publish
from fastapi import Depends, UploadFile
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from typing import Optional
from datetime import datetime, timezone
from math import ceil
from bson import ObjectId
from databases.mongodb import get_firmware_collection

from cores.service_drive import upload_to_drive
from dtos.dto_firmware import UploadFirmwareForm, UpdateFirmwareForm, UpdateFirmwareDescriptionForm, OutputFirmwarePagination, OuputFirmwareByNodeName
from repositories.repository_firmware import FirmwareRepository

load_dotenv()
MQTT_ADDRESS = os.getenv("MQTT_ADDRESS")

def get_firmware_repository():
    return FirmwareRepository(get_firmware_collection())

class ServiceFirmware:
    def __init__(self, firmware_repository: FirmwareRepository = Depends(get_firmware_repository)):
        self.firmware_repository = firmware_repository
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
        print("DEBUG folder_id:", repr(self.folder_id))

    async def get_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None,
        sensor_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> OutputFirmwarePagination:
        try:
            # 1. Data firmware
            list_firmware = await self.firmware_repository.get_list_firmware(
                page=page,
                per_page=per_page,
                node_id=node_id,
                node_location=node_location,
                sensor_type=sensor_type
            )

            # 2. Total data
            total_data = await self.firmware_repository.count_list_firmware(
                node_id=node_id,
                node_location=node_location,
                sensor_type=sensor_type
            )

            # 3. Total page
            total_page = ceil(total_data / per_page) if total_data else 1

            # 4. Get filter options
            filter_options = await self.firmware_repository.get_filter_options()

            # 5. Return response
            return OutputFirmwarePagination(
                page=page,
                per_page=per_page,
                total_data=total_data,
                total_page=total_page,
                filter_options=filter_options,
                firmware_data=list_firmware
            )
        except Exception as e:
            return HTTPException(status_code=500, detail=f"Gagal mengambil data firmware: {str(e)}")

    async def get_by_node_name(
            self,
            node_name: str,
            page: int = 1,
            per_page: int = 10
    ) -> OuputFirmwareByNodeName:
        try:
            list_firmware = await self.firmware_repository.get_by_node_name(
                node_name=node_name,
                page=page,
                per_page=per_page
            )

            total_data = await self.firmware_repository.count_by_node_name(node_name)
            total_page = ceil(total_data / per_page) if total_data else 1

            return OuputFirmwareByNodeName(
                page=page,
                per_page=per_page,
                total_data=total_data,
                total_page=total_page,
                firmware_data=list_firmware
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gagal mengambil data firmware berdasarkan node_name: {str(e)}")

    async def add_firmware(self, form: UploadFirmwareForm):
        filename = form.firmware_file.filename
        save_path = f"tmp/{filename}"
        
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
            
        try:
            with open(save_path, "wb+") as f:
                content = await form.firmware_file.read()
                f.write(content)
        except Exception as e:
            raise Exception(f"Gagal menyimpan file: {str(e)}")
        
        #Upload Ke GDrive
        try:
            firmware_url = upload_to_drive(save_path, filename, self.folder_id)
        except Exception as e:
            raise Exception(f"Gagal Upload ke GDrive: {str(e)}")
        
        firmware_dto = form.to_dto(firmware_url)
        firmware_data = firmware_dto.model_dump()
        firmware_data["latest_updated"] = datetime.now(timezone.utc)

        #Make node_name
        node_location = firmware_data.get("node_location", "Unknown")
        node_id = firmware_data.get("node_id", "0")
        sensor_type = firmware_data.get("sensor_type", "Unknown")
        node_name = f"{node_location}-node{node_id}".lower()
        firmware_version = firmware_data.get("firmware_version", "1.0.0")
        firmware_data["node_name"] = node_name

        #Input to MongoDB
        try:
            await self.firmware_repository.add_firmware(firmware_data)
        except Exception as e:
            raise Exception(f"Gagal input ke MongoDB: {str(e)}")
        
        #Publish ke MQTT
        try:
            topic = "LokaSync/CloudOTA/Firmware"
            payload = json.dumps({
                "node_name":node_name,
                "firmware_version": firmware_version,
                "url": firmware_url
            })
            publish.single(topic, payload, hostname=MQTT_ADDRESS)
        except Exception as e:
            raise Exception(f"Gagal Mengirim ke MQTT: {str(e)}")
        
    async def update_firmware(self, node_name: str, form: UpdateFirmwareForm):
        filename = form.firmware_file.filename
        save_path = f"tmp/{filename}"
        
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        
        try:
            with open(save_path, "wb+") as f:
                content = await form.firmware_file.read()
                f.write(content)
        except Exception as e:
            raise Exception(f"Gagal menyimpan file: {str(e)}")
            
        try:
            firmware_url = upload_to_drive(save_path, filename, self.folder_id)
        except Exception as e:
            raise Exception(f"Gagal Upload ke GDrive: {str(e)}")
        
        try:
            new_data = await self.firmware_repository.update_firmware(
                node_name,
                {
                    "firmware_description": getattr(form, "firmware_description", ""),
                    "firmware_version": form.firmware_version,
                    "firmware_url": firmware_url,
                })
            if not new_data:
                raise HTTPException(status_code=404, detail="Firmware not found")
        except Exception as e:
            raise Exception(f"Gagal input ke MongoDB: {str(e)}")
        
        try:
            topic = "LokaSync/CloudOTA/Firmware"
            payload = json.dumps({
                "node_name": node_name,
                "url": firmware_url,
                "firmware_version": form.firmware_version
            })
            publish.single(topic, payload, hostname=MQTT_ADDRESS)
        except Exception as e:
            raise Exception(f"Gagal Mengirim ke MQTT: {str(e)}")
        
        return {"message": "Update firmware successfully."}
    
    async def update_firmware_description(
            self,
            node_name: str,
            firmware_version: str,
            form: UpdateFirmwareDescriptionForm
    ):
        try:
            updated = await self.firmware_repository.update_firmware_description(
                node_name,
                firmware_version,
                {
                    "firmware_description": form.firmware_description,
                }
            )
            if not updated:
                raise HTTPException(status_code=404, detail="Firmware not found")
        except Exception as e:
            raise Exception(f"Gagal input ke MongoDB: {str(e)}")
        
    async def delete_by_firmware_version(
            self, 
            node_name: str,
            firmware_version
    ):
        await self.firmware_repository.delete_by_firmware_verison(node_name, firmware_version)

    async def delete_all_by_node_name(self, node_name: str):
        await self.firmware_repository.delete_all_by_node_name(node_name)