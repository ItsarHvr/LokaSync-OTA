from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from bson import ObjectId

from models.common import PyObjectId
from utils.datetime import (
    set_default_timezone,
    convert_datetime_to_str
)
from utils.validator import (
    validate_input,
    sanitize_input
)


class NodeModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime = Field(..., default_factory=set_default_timezone)
    latest_updated: datetime = Field(..., default_factory=set_default_timezone)
    node_location: str = Field(
        ...,
        min_length=3,
        max_length=255,
    )
    node_type: str = Field(
        ...,
        min_length=3,
        max_length=255,
    )
    node_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )
    node_codename: str = Field(
        ...,
        min_length=3,
        max_length=255
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    firmware_url: Optional[str] = Field(
        ...,
        pattern=r'^https?://.*$',
        min_length=15
    )
    firmware_version: Optional[str] = Field(
        ...,
        pattern=r'^\d+\.\d+$',
        min_length=3,
        max_length=10
    )

    @field_validator("node_location", "node_type", "node_id")
    def validate_node_location(cls, v):
        return validate_input(v)

    @field_validator("description")
    def validate_description(cls, v):
        if v is not None:
            return sanitize_input(v)
        return v


    class Config:
        """
        Configuration for the Location Model.
        
        Settings:
            validate_assignment: Ensures that field values are validated when assigned.
            populate_by_name: Allows the model to populate fields using the field's alias.
            validate_by_name: Allows the model to populate fields using the field's alias.
            arbitrary_types_allowed: Allows the use of arbitrary Python types like ObjectId.
            json_encoders: Custom JSON encoder for ObjectId to convert it to a string.
        """
        validate_assignment = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = { ObjectId: str, datetime: convert_datetime_to_str }
        json_schema_extra = {
            "example": {
                "_id": "123456789",
                "created_at": "2023-10-01T12:00:00+07:00",
                "latest_updated": "2023-10-01T12:00:05+07:00",
                "node_location": "Cibubur-SayuranPagi",
                "node_type": "Pembibitan",
                "node_id": "1a",
                "node_codename": "cibubur-sayuranpagi_pembibitan_1a",
                "description": "This is a description of the node.",
                "firmware_url": "https://example.com/firmware/example.ino.bin",
                "firmware_version": "1.0"
            }
        }