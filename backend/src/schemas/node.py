from pydantic import BaseModel, Field, field_validator
from fastapi import File, UploadFile
from typing import Optional, List

from models.node import NodeModel
from schemas.common import (
    BaseAPIResponse,
    BasePagination,
    BaseFilterOptions
)
from cores.config import env
from utils.validator import validate_input


class NodeCreateSchema(BaseModel):
    """ Add a new node location. """
    
    node_location: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Location identifier for the node (e.g., Cibubur - Sayuran Pagi, etc.)"
    )
    node_type: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Type of the node (e.g., Penyemaian, Pembibitan, etc.)"
    )
    node_id: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Type of the node (e.g., 1a, 1b, 2c, etc.)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional description for the node"
    )

    @field_validator("node_location")
    def validate_node_location(cls, v):
        return validate_input(v)

    @field_validator("node_type")
    def validate_node_type(cls, v):
        return validate_input(v)

    @field_validator("node_id")
    def validate_node_id(cls, v):
        return validate_input(v)


    class Config:
        json_schema_extra = {
            "example": {
                "node_location": "Cibubur - SayuranPagi",
                "node_type": "Penyemaian",
                "node_id": "1a",
                "description": "Kebun sayuran di Cibubur",
            }
        }


class NodeModifyVersionSchema(BaseModel):
    """
    Add and update firmware version for a node.
    
    - Add first firmware version of the existing node. (PUT)
    - Add new firmware version of a specific node. (POST)
    """

    firmware_version: str = Field(
        ...,
        pattern=r'^\d+\.\d+$',
        min_length=3,
        max_length=20,
        description="Firmware version in x.y format (e.g., 1.0)"
    )
    firmware_url: Optional[str] = Field(
        default=None,
        min_length=15,
        pattern=r'^https?://.*$',
        description="Direct URL to the firmware file (provide if not uploading a file)"
    )
    firmware_file: UploadFile = File(
        default=None,
        media_type="application/octet-stream",
        max_length=f"{env.UPLOAD_FILE_MAX_SIZE_MB}" * 1024 * 1024
    )
    
    class Config:
        """
        Configuration for the NodeUpdateSchema.
        This allows for extra fields to be ignored.
        """
        json_schema_extra = {
            "example": {
                "firmware_url": "https://example.com/firmware/example.ino.bin",
                "firmware_version": "1.0",
                "firmware_file": None
            }
        }


class NodeResponse(BaseAPIResponse, BasePagination):
    """
    Response schema for a location.
    Contains the location details and an optional description.
    """
    filter_options: Optional[BaseFilterOptions] = None
    data: List[NodeModel]
    
    class Config:
        """
        Configuration for the ResponseLocation schema.
        This allows for extra fields to be ignored.
        """
        json_schema_extra = {
            "example": {
                "message": "Success",
                "status_code": 200,
                "page": 1,
                "page_size": 10,
                "total_data": 0,
                "total_page": 1,
                "filter_options": {
                    "node_locations": [
                        "Kebun Cibubur",
                        "Kebun Bogor"
                    ],
                    "node_type": [
                        "Penyemaian",
                        "Pembibitan"
                    ]
                },
                "data": [
                    {
                        "id": "123456789",
                        "created_at": "2023-10-01T12:00:00+07:00",
                        "latest_updated": "2023-10-01T12:00:05+07:00",
                        "node_location": "Cibubur - SayuranPagi",
                        "node_type": "Penyemaian",
                        "node_id": "1a",
                        "node_codename": "cibubur-sayuranpagi_penyemaian_1a",
                        "description": "This is a description of the location.",
                        "firmware_url": "https://example.com/firmware/example.ino.bin",
                        "firmware_version": "1.0"
                    }
                ]
            }
        }


class SingleNodeResponse(BaseAPIResponse):
    data: Optional[NodeModel] = None

    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "id": "123456789",
                    "created_at": "2023-10-01T12:00:00+07:00",
                    "latest_updated": "2023-10-01T12:00:05+07:00",
                    "node_location": "Cibubur - SayuranPagi",
                    "node_type": "Penyemaian",
                    "node_id": "1a",
                    "node_codename": "cibubur-sayuranpagi_penyemaian_1a",
                    "description": "This is a description of the location.",
                    "firmware_url": "https://example.com/firmware/example.ino.bin",
                    "firmware_version": "1.0"
                }
            }
        }