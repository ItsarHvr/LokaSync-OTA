import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from math import ceil

from fastapi import Depends, UploadFile
from fastapi.exceptions import HTTPException
from dotenv import load_dotenv
import paho.mqtt.publish as publish

from databases.mongodb import get_firmware_collection
from cores.service_drive import upload_to_drive
from dtos.dto_firmware import (
    UploadFirmwareForm, 
    UpdateFirmwareForm, 
    UpdateFirmwareDescriptionForm, 
    OutputFirmwarePagination, 
    OuputFirmwareByNodeName
)
from repositories.repository_firmware import FirmwareRepository

# ========== INITIAL SETUP ==========
logger = logging.getLogger(__name__)
load_dotenv()

MQTT_ADDRESS = os.getenv("MQTT_ADDRESS")
TMP_DIR = Path(os.getenv("TMP_DIR", "tmp"))


# ========== DEPENDENCY INJECTION ==========
def get_firmware_repository():
    return FirmwareRepository(get_firmware_collection())

# ========== SERVICE ==========
class ServiceFirmware:
    def __init__(self, firmware_repository: FirmwareRepository = Depends(get_firmware_repository)):
        self.firmware_repository = firmware_repository
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
        self.mqtt_topic = os.getenv("MQTT_TOPIC_CLOUD_OTA", "LokaSync/CloudOTA/Firmware")
        logger.debug(f"folder_id: {repr(self.folder_id)}")

    # ---------- PRIVATE METHODS ----------

    async def _save_file_to_tmp(self, file: UploadFile) -> Path:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        save_path = TMP_DIR / file.filename
        try:
            with open(save_path, "wb+") as f:
                content = await file.read()
                f.write(content)
            return save_path
        except Exception as e:
            logger.error(f"Failed saving file : {e}")
            raise Exception(f"Gagal menyimpan file: {str(e)}")
        
    def _upload_and_cleanup(self, path: str, filename: str) -> str:
        try:
            url = upload_to_drive(path, filename, self.folder_id)
            path.unlink()
            return url
        except Exception as e:
            logger.error(f"Upload to GDrive failed: {e}")
            raise Exception(f"Gagal Upload ke GDrive: {str(e)}")
        
    def _publish_to_mqtt(self, payload:dict):
        try:
            publish.single(self.mqtt_topic, json.dumps(payload), hostname=MQTT_ADDRESS)
            logger.info(f"MQTT published to {self.mqtt_topic}: {payload}")
        except Exception as e:
            logger.error(f"MQTT publish failed: {e}")
            raise Exception(f"Gagal mengirim ke MQTT: {str(e)}")
        
    def _generate_node_codename(self, data: dict) -> str:
        loc = data.get("node_location", "Unknown").lower()
        id_ = data.get("node_id", "Unknown").lower()
        type_ = data.get("node_type", "Unknown").lower()
        is_group = data.get("is_group", False)
        return f"{loc}_{type_}_group{id_}" if is_group else f"{loc}_{type_}_{id_}"
    
    async def _proccess_and_publish_firmware(self, form_file: UploadFile, metadata: dict) -> tuple[str, dict]:
        save_path = await self._save_file_to_tmp(form_file)
        firmware_url = self._upload_and_cleanup(save_path, form_file.filename)
        metadata["latest_updated"] = datetime.now(timezone.utc)
        node_codename = self._generate_node_codename(metadata)
        metadata["node_codename"] = node_codename
        metadata["firmware_url"] = firmware_url

        self._publish_to_mqtt({
            "node_codename": node_codename,
            "firmware_version": metadata.get("firmware_version", "1.0.0"),
            "url": firmware_url
        })

        return firmware_url, metadata
    
    # ---------- PUBLIC METHODS ----------

    async def get_list_firmware(
        self,
        node_id: Optional[str] = None,
        node_location: Optional[str] = None,
        node_type: Optional[str] = None,
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
                node_type=node_type
            )

            # 2. Total data
            total_data = await self.firmware_repository.count_list_firmware(
                node_id=node_id,
                node_location=node_location,
                node_type=node_type
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
            logger.error(f"Gagal mengambil data firmware: {e}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil data firmware: {str(e)}")

    async def get_by_node_name(
            self,
            node_codename: str,
            page: int = 1,
            per_page: int = 10
    ) -> OuputFirmwareByNodeName:
        try:
            list_firmware = await self.firmware_repository.get_by_node_name(
                node_codename=node_codename,
                page=page,
                per_page=per_page
            )

            total_data = await self.firmware_repository.count_by_node_name(node_codename)
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
        try:
            form_dict = {
            "firmware_version": form.firmware_version,
            "node_location": form.node_location,
            "node_id": form.node_id,
            "firmware_description": form.firmware_description,
            "node_type": form.node_type,
            "is_group": form.is_group
            }
            firmware_url, metadata = await self._proccess_and_publish_firmware(form.firmware_file, form_dict)
            await self.firmware_repository.add_firmware(metadata)
        except Exception as e:
            logger.error(f"Gagal menambahkan firmware: {e}")
            raise Exception(f"Gagal input ke MongoDB: {str(e)}")

    async def update_firmware(self, node_codename: str, form: UpdateFirmwareForm):
        try:
            save_path = await self._save_file_to_tmp(form.firmware_file)
            firmware_url = self._upload_and_cleanup(save_path, form.firmware_file.filename)

            new_data = await self.firmware_repository.update_firmware(
                node_codename,
                {
                    "firmware_description": getattr(form, "firmware_description", ""),
                    "firmware_version": form.firmware_version,
                    "firmware_url": firmware_url,
                })
            if not new_data:
                raise HTTPException(status_code=404, detail="Firmware not found")
            
            self._publish_to_mqtt({
                "node_codename": node_codename,
                "firmware_version": form.firmware_version,
                "url": firmware_url
            })

            return {"message": "Update firmware successfully."}
        except Exception as e:
            logger.error(f"Gagal update firmware: {e}")
            raise Exception(f"Gagal input ke MongoDB: {str(e)}")
    
    async def update_firmware_description(
            self,
            node_codename: str,
            firmware_version: str,
            form: UpdateFirmwareDescriptionForm
    ):
        try:
            updated = await self.firmware_repository.update_firmware_description(
                node_codename,
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
            node_codename: str,
            firmware_version
    ):
        await self.firmware_repository.delete_by_firmware_version(node_codename, firmware_version)

    async def delete_all_by_node_name(self, node_codename: str):
        await self.firmware_repository.delete_all_by_node_name(node_codename)