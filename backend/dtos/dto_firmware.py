from pydantic import BaseModel, Field
from typing import Optional, List, TypedDict
from fastapi import Form, UploadFile, File

from dtos.dto_common import BasePage
from models.model_firmware import Firmware


class InputFirmware(BaseModel):
    firmware_description: Optional[str] = Field(min_length=1, max_length=255)
    firmware_version: str = Field(min_length=1, max_length=8, pattern=r'^\d+\.\d+\.\d+$') # MAJOR.MINOR.PATCH
    firmware_url: str = Field(min_length=1, pattern=r'^(http|https)://.*$') # URL FORMAT
    node_id: str = Field(min_length=1, max_length=255)
    node_location: str = Field(min_length=1, max_length=255)
    node_type: str = Field(min_length=1, max_length=255)
    is_group: bool = False

    class Config:
        json_schema_extra ={
            "example": {
                "firmware_version": "1.0.0",
                "firmware_url": "https://example.com/firmware/node_location/firmware.ino.bin",
                "firmware_description": "This is a firmware description.",
                "node_id": 1,
                "node_location": "Depok Greenhouse"
            }
        }

class UploadFirmwareForm:
    def __init__(
        self,
        firmware_version: str = Form(...),
        node_location : str = Form(...),
        node_id: str = Form(...),
        firmware_description : str = Form(...),
        node_type : str = Form(...),
        is_group: bool = Form(False),
        firmware_file : UploadFile = File(...)
    ):
        self.firmware_version = firmware_version
        self.node_id = node_id
        self.node_location = node_location
        self.firmware_description = firmware_description
        self.firmware_file = firmware_file
        self.node_type = node_type
        self.is_group = is_group
        
    def to_dto(self, firmware_url: str) -> InputFirmware:
        return InputFirmware(
            firmware_description=self.firmware_description,
            firmware_version=self.firmware_version,
            firmware_url=firmware_url,
            node_id=self.node_id,
            node_location=self.node_location,
            node_type=self.node_type,
            is_group=self.is_group
        )
        
class UpdateFirmwareForm:
    def __init__(
        self,
        firmware_version: str = Form(...),
        firmware_file : UploadFile = File(...),
        firmware_description : Optional[str] = Form(None),
    ):
        self.firmware_version = firmware_version
        self.firmware_file = firmware_file
        self.firmware_description = firmware_description
        
    def to_dto(self, firmware_url: str) -> InputFirmware:
        return InputFirmware(
            firmware_version=self.firmware_version,
            firmware_url=firmware_url,
            firmware_description=self.firmware_description,
        )

class UpdateFirmwareDescriptionForm:
    def __init__(
        self,
        firmware_description: str = Form(...),
    ):
        self.firmware_description = firmware_description

    def to_dto(self) -> InputFirmware:
        return InputFirmware(
            firmware_description=self.firmware_description
        )

class FilterOptions(TypedDict):
    node_id: List[str]
    node_location: List[str]
    node_type: List[str]

class OutputFirmwarePagination(BasePage):
    page: int
    per_page: int
    total_data: int
    total_page: int
    filter_options: FilterOptions = Field(default_factory=lambda: {
        "node_id": [], 
        "node_location": [],
        "node_type": []
    })
    firmware_data: List[Firmware] = Field(default_factory=list)

class OuputFirmwareByNodeName(BasePage):
    page: int
    per_page: int
    total_data: int
    total_page: int
    firmware_data: List[Firmware] = Field(default_factory=list)