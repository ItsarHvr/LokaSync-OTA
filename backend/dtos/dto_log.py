from pydantic import BaseModel, Field
from typing import Optional, List, TypedDict, Any, Dict

from dtos.dto_common import BasePage
from models.model_log import Log

class InputLog(BaseModel):
    type: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1, max_length=255)
    node_name: str = Field(min_length=1, max_length=255)
    firmware_version: str = Field(min_length=1, max_length=255)
    data: Optional[Dict[str, Any]] = None

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
    node_name: List[str]
    firmware_version: List[str]

class OutputLogPagination(BasePage):
    filter_options: FilterOption = Field(default_factory=lambda:{
        "node_name": [], 
        "firmware_version": []
        })
    log_data: List[Log] = Field(default_factory=list)
