from fastapi import File, UploadFile, Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Optional, List

from cores.config import env
from models.node import NodeModel
from schemas.common import (
    BaseAPIResponse,
    BasePagination,
    BaseFilterOptions
)
from utils.validator import (
    validate_input,
    sanitize_input,
    validate_version,
    validate_url
)


class NodeCreateSchema(BaseModel):
    """ Add a new node location. """
    
    node_location: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Location identifier for the node (e.g., Cibubur-SayuranPagi, etc.)"
    )
    node_type: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Type of the node (e.g., Penyemaian, Pembibitan, etc.)"
    )
    node_id: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Specific node id (e.g., 1a, 1b, 2c, etc.)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional description for the node"
    )

    @field_validator("node_location", "node_type", "node_id")
    def validate_node_input(cls, v):
        return validate_input(v)

    @field_validator("description")
    def validate_description(cls, v):
        if v is not None:
            return sanitize_input(v)
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "node_location": "Cibubur-SayuranPagi",
                "node_type": "Pembibitan",
                "node_id": "1a",
                "description": "This is a description of the location.",
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
        max_length=20,
        description="Firmware version in x.y.z format (e.g., 1.0.0)"
    )
    firmware_url: Optional[str] = Field(
        default=None,
        description="Direct URL to the firmware file (if firmware file is not provided)"
    )
    firmware_file: Optional[UploadFile] = Field(
        default=None,
        description="Firmware file to upload (if firmware_url is not provided)"
    )

    @classmethod
    def as_form(
        cls,
        firmware_version: str = Form(
            ..., 
            max_length=20,
            description="Firmware version in x.y.z format (e.g., 1.0.0)"
        ),
        firmware_url: Optional[str] = Form(
            default=None,
            description="Direct URL to the firmware file (if firmware file is not provided)"
        ),
        firmware_file: Optional[UploadFile] = File(
            default=None,
            description="Firmware file to upload (if firmware_url is not provided)"
        )
    ):
        """ Create an instance of NodeModifyVersionSchema from form data."""
        try:
            return cls(
                firmware_version=firmware_version,
                firmware_url=firmware_url,
                firmware_file=firmware_file
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())
    
    @field_validator("firmware_version")
    def validate_firmware_version(cls, v):
        return validate_version(v)

    @field_validator("firmware_url")
    def validate_firmware_url(cls, v):
        if v is not None:
            return validate_url(v)
        return v
    
    @field_validator("firmware_file")
    def validate_firmware_file(cls, v):
        # Handle empty file uploads
        if v and hasattr(v, 'filename') and (v.filename == '' or v.filename is None):
            return None
        return v


    class Config:
        json_schema_extra = {
            "example": {
                "firmware_version": "1.0.0",
                "firmware_url": "https://example.com/firmware/example.ino.bin",
                "firmware_file": None  # Optional, can be a file upload
            }
        }


class NodeResponse(BaseAPIResponse, BasePagination):
    """
    Response schema for a location.
    Contains the location details and an optional description.
    """
    filter_options: BaseFilterOptions = {}
    data: List[NodeModel] = []

    class Config:
        json_schema_extra = {
            "example": {
                "message": "List of nodes retrieved successfully",
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
                    "node_types": [
                        "Penyemaian",
                        "Pembibitan"
                    ]
                },
                "data": [
                    {
                        "_id": "123456789",
                        "created_at": "2023-10-01T12:00:00+07:00",
                        "latest_updated": "2023-10-01T12:00:05+07:00",
                        "node_location": "Cibubur-SayuranPagi",
                        "node_type": "Pembibitan",
                        "node_id": "1a",
                        "node_codename": "cibubur-sayuranpagi_pembibitan_1a",
                        "description": "This is a description of the location.",
                        "firmware_url": "https://example.com/firmware/example.ino.bin",
                        "firmware_version": "1.0.0"
                    }
                ]
            }
        }


class SingleNodeResponse(BaseAPIResponse):
    data: Optional[NodeModel] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Detail node retrieved successfully",
                "status_code": 200,
                "data": {
                    "_id": "123456789",
                    "created_at": "2023-10-01T12:00:00+07:00",
                    "latest_updated": "2023-10-01T12:00:05+07:00",
                    "node_location": "Cibubur-SayuranPagi",
                    "node_type": "Pembibitan",
                    "node_id": "1a",
                    "node_codename": "cibubur-sayuranpagi_pembibitan_1a",
                    "description": "This is a description of the location.",
                    "firmware_url": "https://example.com/firmware/example.ino.bin",
                    "firmware_version": "1.0.0"
                }
            }
        }


class FirmwareVersionListResponse(BaseAPIResponse):
    data: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "List of firmware versions retrieved successfully",
                "status_code": 200,
                "data": [
                    "1.0",
                    "1.1",
                    "2.0"
                ]
            }
        }