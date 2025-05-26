from pydantic import BaseModel, Field
from typing import Optional, List, TypedDict
from fastapi import UploadFile, File

from schemas.common import BasePagination, BaseFilterOptions
from models.firmware import FirmwareModel
from enums.common import NodeLocation


# /api/v1/firmware/add
class InputFirmware(BaseModel):
    firmware_description: Optional[str] = Field(min_length=1, max_length=255)
    firmware_file: UploadFile = File(
        media_type="application/octet-stream",
        max_length=2 * 1024 * 1024,  # 2 MB max file size
        description="Firmware file to be uploaded"
    )
    firmware_version: str = Field(min_length=1, max_length=8, pattern=r'^\d+\.\d+\.\d+$')
    firmware_url: Optional[str] = Field(min_length=1, pattern=r'^(http|https)://.*$')
    node_id: int = Field(ge=1)
    node_location: NodeLocation = Field(min_length=1, max_length=255)


    class Config:
        json_schema_extra ={
            "example": {
                "firmware_description": "This is a firmware description.",
                "firmware_file": {
                    "filename": "firmware.ino.bin",
                    "content_type": "application/octet-stream",
                    "size": 2 * 1024 * 1024  # 2 MB
                },
                "firmware_version": "1.0.0",
                "firmware_url": "https://example.com/firmware/firmware.ino.bin",
                "node_id": 1,
                "node_location": "Depok Greenhouse"
            }
        }


# /api/v1/firmware/update/{node_name}
class UpdateFirmware(BaseModel):
    firmware_description: Optional[str] = Field(min_length=1, max_length=255)
    firmware_file: UploadFile = File(
        media_type="application/octet-stream",
        max_length=2 * 1024 * 1024,  # 2 MB max file size
        description="Firmware file to be uploaded"
    )
    firmware_version: str = Field(min_length=1, max_length=8, pattern=r'^\d+\.\d+\.\d+$')
    firmware_url: Optional[str] = Field(min_length=1, pattern=r'^(http|https)://.*$')


    class Config:
        json_schema_extra = {
            "example": {
                "firmware_description": "This is an updated firmware description.",
                "firmware_file": {
                    "filename": "updated_firmware.ino.bin",
                    "content_type": "application/octet-stream",
                    "size": 2 * 1024 * 1024  # 2 MB
                },
                "firmware_version": "1.0.1",
                "firmware_url": "https://example.com/firmware/updated_firmware.ino.bin"
            }
        }


# /api/v1/firmware/update/description/{node_name}
class UpdateFirmwareDescription(BaseModel):
    firmware_description: str = Field(min_length=1, max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "firmware_description": "This is an updated firmware description."
            }
        }


# /api/v1/firmware
class OutputFirmwarePagination(BasePagination):
    filter_options: List[BaseFilterOptions] = Field(
        default_factory=lambda: {
            "node_id": [],
            "node_location": [l.value for l in NodeLocation],
        }
    )
    firmware_data: List[FirmwareModel] = Field(default_factory=list)


# /api/v1/firmware/{node_name}
class OuputFirmwareByNodeName(BaseModel):
    list_firmware_version: List[str] = Field(default_factory=list)


# class UploadFirmwareForm:
#     def __init__(
#         self,
#         firmware_version: str = Form(...),
#         node_location : str = Form(...),
#         node_id: int = Form(...),
#         firmware_description : str = Form(...),
#         sensor_type : str = Form(...),
#         firmware_file : UploadFile = File(...)
#     ):
#         self.firmware_version = firmware_version
#         self.node_id = node_id
#         self.node_location = node_location
#         self.firmware_description = firmware_description
#         self.firmware_file = firmware_file
#         self.sensor_type = sensor_type
        
#     def to_dto(self, firmware_url: str) -> InputFirmware:
#         return InputFirmware(
#             firmware_description=self.firmware_description,
#             firmware_version=self.firmware_version,
#             firmware_url=firmware_url,
#             node_id=self.node_id,
#             node_location=self.node_location,
#             sensor_type=self.sensor_type
#         )
        
# class UpdateFirmwareForm:
#     def __init__(
#         self,
#         firmware_version: str = Form(...),
#         firmware_file : UploadFile = File(...),
#         firmware_description : Optional[str] = Form(None),
#     ):
#         self.firmware_version = firmware_version
#         self.firmware_file = firmware_file
#         self.firmware_description = firmware_description
        
#     def to_dto(self, firmware_url: str) -> InputFirmware:
#         return InputFirmware(
#             firmware_version=self.firmware_version,
#             firmware_url=firmware_url,
#             firmware_description=self.firmware_description,
#         )

# class UpdateFirmwareDescriptionForm:
#     def __init__(
#         self,
#         firmware_description: str = Form(...),
#     ):
#         self.firmware_description = firmware_description

#     def to_dto(self) -> InputFirmware:
#         return InputFirmware(
#             firmware_description=self.firmware_description
#         )