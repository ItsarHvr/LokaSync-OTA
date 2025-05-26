from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

from cores.config import env
from models.common import PyObjectId
from enums.log import LogStatus
from enums.common import NodeLocation


class LogModel(BaseModel):
    """
    A Pydantic model representing a log document in MongoDB.

    Data sent from ESP devices to backend through MQTTS, then from backend to database.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", description="Unique identifier for the log document")
    node_id: int = Field(default=1, ge=1, description="Unique identifier for the node that this log is associated with")
    node_location: str = Field(
        default=NodeLocation.DEPOK_GREENHOUSE,
        max_length=255,
        description="Location of the node that this log is associated with"
    )
    node_name: str = Field(
        default="depok-node1",
        max_length=100,
        description="A unique name for the node that this log is associated with",
    )
    first_version: str = Field(default="1.0.0", max_length=50, description="First version of the firmware associated with this log")
    latest_version: Optional[str] = Field(default=None, max_length=50, description="Latest version of the firmware associated with this log")
    firmware_url: str = Field(
        default="http://example.com/firmware.ino.bin",
        description="URL to download the firmware binary file associated with this log",
    )
    # For QoS purpose
    firmware_size: int = Field(default=0, ge=0, description="Size of the firmware file in bytes")
    download_duration: float = Field(
        default=0.0,
        ge=0.0,
        description="Duration of the firmware download in seconds",
    )
    download_speed: float = Field(default=0.0, ge=0.0, description="Download speed of the firmware file in bytes per second")
    download_completed: datetime = Field(
        default_factory=lambda: datetime.now(timezone.tzname(env.TIMEZONE)),
        description="Timestamp when the firmware download was completed"
    )
    flash_completed: datetime = Field(
        default_factory=lambda: datetime.now(timezone.tzname(env.TIMEZONE)),
        description="Timestamp when the firmware flashing was completed"
    )
    status: LogStatus = Field(default=LogStatus.SUCCESS, description="Status of the log entry")
    # Additional data from backend
    latest_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.tzname(env.TIMEZONE)),
        description="Timestamp when the log document was last updated"
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
        json_encoders = {datetime: lambda d: d.isoformat()}
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1e8b001c8e4d3a",
                "node_id": 1,
                "node_location": NodeLocation.DEPOK_GREENHOUSE,
                "node_name": "depok-node1",
                "first_version": "1.0.0",
                "latest_version": "1.0.1",
                "firmware_url": "http://example.com/firmware.ino.bin",
                "firmware_size": 102400,
                "download_duration": 5.0,
                "download_speed": 20480.0,
                "download_completed": "2023-10-01T12:00:00+07:00",
                "flash_completed": "2023-10-01T12:00:05+07:00",
                "status": LogStatus.SUCCESS,
                "latest_updated": "2023-10-01T12:00:05+07:00"
            }
        }