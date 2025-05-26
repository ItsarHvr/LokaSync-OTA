from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from models.common import PyObjectId
from cores.config import env
from enums.common import NodeLocation


class FirmwareModel(BaseModel):
    """
    A Pydantic model representing a firmware document in MongoDB.

    Data sent from backend to database.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", description="Unique identifier for the firmware document")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.tzname(env.TIMEZONE)),
        description="Timestamp when the firmware document was created"
    )
    firmware_description: Optional[str] = Field(default=None, max_length=500, description="Description of the firmware")
    firmware_version: str = Field(default="1.0.0", max_length=10, description="Version of the firmware")
    firmware_url: str = Field(default="http://example.com/firmware.ino.bin", description="URL to download the firmware binary file")
    latest_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.tzname(env.TIMEZONE)),
        description="Timestamp when the firmware document was last updated"
    )
    node_id: int = Field(default=1, ge=1, description="Unique identifier for the node that this firmware is associated with")
    node_location: str = Field(
        default=NodeLocation.DEPOK_GREENHOUSE,
        max_length=255,
        description="Location of the node that this firmware is associated with",
    )
    node_name: str = Field(
        default="depok-node1",
        max_length=100,
        description="A unique name for the node that this firmware is associated with",
    )


    class Config:
        """
        Configuration for the Pydantic model.
        
        Settings:
            validate_by_name: Allows the model to populate fields using the field's alias.
            arbitrary_types_allowed: Allows the use of arbitrary Python types like ObjectId.
            json_encoders: Custom JSON encoder for ObjectId to convert it to a string.
        """
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = { datetime: lambda d: d.isoformat() }
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1e8b001c8e4d3a",
                "created_at": "2023-10-01T12:00:00+07:00",
                "latest_updated": "2023-10-01T12:00:00+07:00",
                "firmware_description": "Firmware for temperature and humidity sensor",
                "firmware_version": "1.0.0",
                "firmware_url": "http://example.com/firmware.ino.bin",
                "node_id": 1,
                "node_location": NodeLocation.DEPOK_GREENHOUSE,
                "node_name": "depok-node1"
            }
        }
