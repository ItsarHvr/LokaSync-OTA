from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId

from models.common import PyObjectId
from enums.log import LogStatus
from utils.datetime import set_default_timezone, convert_datetime_to_str


class LogModel(BaseModel):
    """
    A Pydantic model representing a log document in MongoDB.

        Data sent from ESP devices to backend through MQTTS broker, then from backend to database.
        ... means this field is required.
    """
    id: Optional[PyObjectId] = Field(
        ...,
        default_factory=None,
        alias="_id",
        description="Unique identifier for the log document"
    )
    # Additional log data from backend
    created_at: datetime = Field(
        ...,
        default_factory=set_default_timezone,
        description="Timestamp when the log document was created"
    )
    latest_updated: Optional[datetime] = Field(
        ...,
        default_factory=set_default_timezone,
        description="Timestamp when the log document was last updated"
    )
    # General log data
    greeenhouse_location: str = Field(
        ...,
        min_length=3,
        description="Location of the node that this log is associated with"
    )
    greenhouse_name: str = Field(
        ...,
        min_length=3,
        description="Specific location within the greenhouse that this log is associated with", 
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
        description="A unique name for the node that this log is associated with",
    )
    first_version: str = Field(
        ...,
        max_length=8,
        description="First version of the firmware associated with this log"
    )
    latest_version: Optional[str] = Field(
        default=None,
        max_length=11,
        description="Latest version of the firmware associated with this log"
    )
    firmware_url: str = Field(
        ...,
        description="URL to download the firmware binary file associated with this log",
    )
    # For QoS purpose
    firmware_size: int = Field(
        ...,
        ge=0,
        description="Size of the firmware file in bytes"
    )
    download_speed: float = Field(
        ...,
        ge=0.0,
        description="Download speed of the firmware file in bytes per second"
    )
    download_completed: datetime = Field(
        ...,
        default_factory=set_default_timezone,
        description="Timestamp when the firmware download was completed"
    )
    download_duration: float = Field(
        ...,
        ge=0.0,
        description="Duration of the firmware download in seconds",
    )
    flash_completed: Optional[datetime] = Field(
        default_factory=set_default_timezone,
        description="Timestamp when the firmware flashing was completed"
    )
    flash_status: LogStatus = Field(..., description="Status of the firmware flashing process")


    class Config:
        """
        Configuration for the Log Model.
        
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
                "id": "123456789",
                "created_at": "2023-10-01T12:00:00+07:00",
                "latest_updated": "2023-10-01T12:00:05+07:00",
                "greeenhouse_location": "Kebun Cibubur",
                "greenhouse_name": "Sayuran Pagi",
                "room_name": "Penyemaian",
                "room_id": "1a",
                "node_id": "kebun-cibubur_sayuran-pagi_penyemaian_room-1a",
                "first_version": "1.0.0",
                "latest_version": "1.0.1",
                "firmware_url": "http://example.com/firmware.ino.bin",
                "firmware_size": 102400,
                "download_speed": 20480.0,
                "download_completed": "2023-10-01T12:00:00+07:00",
                "download_duration": 5.0,
                "flash_completed": "2023-10-01T12:00:05+07:00",
                "flash_status": str(LogStatus.SUCCESS)
            }
        }