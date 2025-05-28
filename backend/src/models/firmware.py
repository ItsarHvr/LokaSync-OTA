from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

from models.common import PyObjectId
from utils.datetime import set_default_timezone, convert_datetime_to_str


class FirmwareModel(BaseModel):
    """
    A Pydantic model representing a firmware document in MongoDB.

        Data sent from backend to database.
        ... means this field is required.
    """
    id: Optional[PyObjectId] = Field(
        ...,
        default_factory=ObjectId,
        alias="_id",
        description="Unique identifier for the firmware document"
    )
    created_at: datetime = Field(
        ...,
        default_factory=set_default_timezone,
        description="Timestamp when the firmware document was created"
    )
    latest_updated: Optional[datetime] = Field(
        default_factory=set_default_timezone,
        description="Timestamp when the firmware document was last updated"
    )
    firmware_description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Description of the firmware"
    )
    firmware_version: str = Field(
        ...,
        max_length=11,
        description="Version of the firmware"
    )
    firmware_url: str = Field(
        ...,
        description="URL to download the firmware binary file"
    )
    greenhouse_location: str = Field(
        ...,
        min_length=3,
        description="Location of the node that this firmware is associated with",
    )
    greenhouse_name: str = Field(
        ...,
        min_length=3,
        description="Specific location within the greenhouse that this firmware is associated with",
    )
    room_name: str = Field(
        ...,
        min_length=3,
        description="Name of the room within the greenhouse location"
    )
    room_id: str = Field(
        ...,
        min_length=2,
        description="Unique identifier for the room within the greenhouse location"
    )
    node_id: str = Field(
        ...,
        min_length=3,
        description="A unique name for the node that this firmware is associated with",
    )


    class Config:
        """
        Configuration for the Firmware Model.
        
        Settings:
            validate_by_name: Allows the model to populate fields using the field's alias.
            arbitrary_types_allowed: Allows the use of arbitrary Python types like ObjectId.
            json_encoders: Custom JSON encoder for ObjectId to convert it to a string.
        """
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: convert_datetime_to_str
        }
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1e8b001c8e4d3a",
                "created_at": "2023-10-01T12:00:00+07:00",
                "latest_updated": "2023-10-01T12:00:00+07:00",
                "firmware_description": "Firmware for temperature and humidity sensor",
                "firmware_version": "1.0.0",
                "firmware_url": "http://example.com/firmware.ino.bin",
                "greeenhouse_location": "Kebun Cibubur",
                "greenhouse_name": "Sayuran Pagi",
                "room_name": "Penyemaian",
                "room_id": "1a",
                "node_id": "kebun-cibubur_sarapan-pagi_penyemaian_room-1a"
            }
        }
