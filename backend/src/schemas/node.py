from urllib.parse import urlparse
from fastapi import File, UploadFile, Form
from pydantic import BaseModel, Field, HttpUrl, field_validator
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
    sanitize_input
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
        pattern=r'^\d+\.\d+(\.\d+)?$',
        max_length=20,
        description="Firmware version in x.y.z format (e.g., 1.0.0)"
    )
    firmware_url: Optional[HttpUrl] = Field(
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
            pattern=r'^\d+\.\d+(\.\d+)?$',
            max_length=20,
            description="Firmware version in x.y.z format (e.g., 1.0.0)"
        ),
        firmware_url: Optional[HttpUrl] = Form(
            default=None,
            description="Direct URL to the firmware file (if firmware file is not provided)"
        ),
        firmware_file: Optional[UploadFile] = File(
            default=None,
            description="Firmware file to upload (if firmware_url is not provided)"
        )
    ):
        """ Create an instance of NodeModifyVersionSchema from form data."""
        return cls(
            firmware_version=firmware_version,
            firmware_url=firmware_url,
            firmware_file=firmware_file
        )

    @field_validator("firmware_url")
    def validate_firmware_url(cls, v):
        # Handle empty strings from form data
        if v is not None and v.strip() == "":
            return None
            
        if v is not None:
            # Basic URL validation using urlparse
            try:
                parsed = urlparse(v)
                
                # Check if scheme is present and valid
                if not parsed.scheme or parsed.scheme not in ['http', 'https']:
                    raise ValueError("URL must start with http:// or https://")
                
                # Check if netloc (domain) is present
                if not parsed.netloc:
                    raise ValueError("URL must contain a valid domain")
                
                # Basic domain validation (should have at least one dot for TLD)
                if '.' not in parsed.netloc:
                    raise ValueError("URL must contain a valid domain with TLD (e.g., .com, .org)")
                
                # Don't sanitize here to preserve URL encoding like %20, %2F, etc.
                return v
                
            except Exception as e:
                raise ValueError(f"Invalid URL format: {str(e)}")
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