from pydantic import BaseModel, Field
from typing import Optional, List, TypedDict, Any, Dict

from dtos.dto_common import BasePage
from models.model_log import Log

class InputLog(BaseModel):
    type: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1, max_length=255)
    node_location: str = Field(min_length=1, max_length=255)
    node_type: str = Field(min_length=1, max_length=255)
    node_codename: str = Field(min_length=1, max_length=255)
    firmware_version: str = Field(min_length=1, max_length=255)
    node_mac: Optional[str] = Field(default=None, min_length=1, max_length=255)
    data: Optional[Dict[str, Any]] = None
    firmware_size: Optional[float] = None
    download_speed: Optional[float] = None
    download_status: str = Field(default="pending", min_length=1, max_length=255)
    ota_status: str = Field(default="pending", min_length=1, max_length=255)

    class Config:
        json_schema_extra ={
            "example": {
            "timestamp": 371764,
            "type": "ota",
            "message": "🔄 OTA update started",
            "node_name": "jakarta-node1-dht22",
            "firmware_version": "1.0.0",
            }
        }

class FilterOption(TypedDict):
    node_location: List[str]
    node_type: List[str]
    ota_status: List[str]

class OutputLogPagination(BasePage):
    filter_options: FilterOption = Field(default_factory=lambda:{
        "node_location": [], 
        "node_type": [],
        "ota_status": []
        })
    log_data: List[Log] = Field(default_factory=list)
