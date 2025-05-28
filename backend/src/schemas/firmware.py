from pydantic import BaseModel
from typing import Optional, List
from fastapi import UploadFile, File, Form

from schemas.common import (
    BaseAPIResponse,
    BasePagination,
    BaseFilterOptions
)
from models.firmware import FirmwareModel
from cores.config import env


class FirmwareSchema(BaseModel):
    """ Schema for add and update firmware version. """
    
    firmware_description: Optional[str] = Form(
        default=None,
        max_length=255,
        description="Description of the firmware"
    )
    firmware_file: Optional[UploadFile] = File(
        media_type='application/octet-stream',
        max_length=env.UPLOAD_FILE_MAX_SIZE_MB * 1024 * 1024,
        description="Firmware file (only .bin supported)"
    )
    firmware_version: Optional[str] = Form(
        pattern=r'^\d+\.\d+\.\d+$',
        min_length=5,
        max_length=10,
        description="Firmware version in format x.y.z"
    )
    firmware_url: Optional[str] = Form(
        default=None,
        pattern=r'^https?://.*$',
        description="URL to download the firmware file"
    )
    greeenhouse_location: Optional[str] = Form(
        min_length=3,
        description="Location of the node that this firmware is associated with"
    )
    greenhouse_name: str = Form(
        min_length=3,
        description="Specific location within the greenhouse that this firmware is associated with"
    )
    room_name: str = Form(
        min_length=3,
        description="Name of the room within the greenhouse location"
    )
    room_id: str = Form(
        min_length=2,
        description="Unique identifier for the room within the greenhouse location"
    )


class InputFirmwareVersionSchema(BaseModel):
    """ Schema for updating firmware version. """
    
    firmware_description: Optional[str] = Form(
        default=None,
        max_length=255,
        description="Description of the firmware"
    )
    firmware_file: UploadFile = File(
        ...,
        media_type='application/octet-stream',
        max_length=env.UPLOAD_FILE_MAX_SIZE_MB * 1024 * 1024,
        description="Firmware binary file (.bin)"
    )
    firmware_version: str = Form(
        ...,
        pattern=r'^\d+\.\d+\.\d+$',
        max_length=10,
        description="Firmware version in format x.y.z"
    )


# class UpdateFirmwareDescriptionSchema(BaseModel):
#     """Schema for updating firmware description only."""
#     firmware_description: str = Form(..., min_length=3, max_length=255)


class ResponseFirmware(BaseAPIResponse, BasePagination):
    """ Paginated firmware response schema. """
    
    filter_options: BaseFilterOptions
    firmware_data: List[FirmwareModel]


    class Config:
        json_schema_extra = {
            "example": {
                "message": "Success",
                "status_code": 200,
                "page": 1,
                "page_size": 10,
                "total_data": 0,
                "total_page": 1,
                "filter_options": {
                    "greeenhouse_locations": [
                        "Kebun Cibubur",
                        "Kebun Bogor"
                    ],
                    "greenhouse_names": [
                        "Sayuran Pagi",
                        "Buah Malam"
                    ],
                    "room_names": [
                        "Penyemaian",
                        "Pembibitan"
                    ]
                },
                "firmware_data": [
                    {
                        "id": "123456789",
                        "created_at": "2023-10-01T12:00:00Z",
                        "latest_updated": "2023-10-01T12:00:00Z",
                        "firmware_description": "Initial firmware version",
                        "firmware_version": "1.0.0",
                        "firmware_url": "http://example.com/firmware.ino.bin",
                        "greeenhouse_location": "Kebun Cibubur",
                        "greenhouse_name": "Sayuran Pagi",
                        "room_name": "Penyemaian",
                        "room_id": "1a",
                        "node_id": "kebun-cibubur_sarapan-pagi_penyemaian_room-1a"
                    }
                ]
            }
        }


class ResponseFirmwareVersion(BaseAPIResponse):
    """ Firmware versions by node name response schema. """
    list_firmware_version: List[str]


    class Config:
        json_schema_extra = {
            "example": {
                "message": "Success",
                "status_code": 200,
                "list_firmware_version": [
                    "1.0.0",
                    "1.0.1",
                    "1.0.2"
                ]
            }
        }