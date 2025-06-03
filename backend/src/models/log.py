from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from bson import ObjectId

from models.common import PyObjectId
from enums.log import LogStatus
from utils.validator import validate_input
from utils.datetime import get_current_datetime, convert_datetime_to_str


class LogModel(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime = Field(..., default_factory=get_current_datetime)
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=255
    )
    node_mac: str = Field(
        ...,
        min_length=12,
    )
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
    firmware_version: str = Field(
        ...,
        pattern=r'^\d+\.\d+\.\d+$',
        min_length=5,
        max_length=20
    )

    # For QoS purpose
    download_started_at: Optional[datetime] = Field(default=None) # OTA update started
    firmware_size_kb: Optional[float] = Field(default=None) # Firmware size OK
    bytes_written: Optional[int] = Field(default=None) # Firmware bytes written
    download_duration_sec: Optional[float] = Field(default=None) # Download time (s)
    download_speed_kbps: Optional[float] = Field(default=None) # Download speed (kB/s)
    download_completed_at: Optional[datetime] = Field(default=None) # Download complete
    flash_completed_at: Optional[datetime] = Field(default=None) # OTA update complete
    flash_status: Optional[LogStatus] = Field(default=LogStatus.IN_PROGRESS) # OTA update complete


    @field_validator("node_location", "node_type", "node_id")
    def validate_node_location(cls, v):
        return validate_input(v)


    class Config:
        """
        Configuration for the Log Model.
        
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
                "session_id": "session-123456789",
                "node_mac": "00:1A:2B:3C:4D:5E",
                "node_location": "Cibubur-SayuranPagi",
                "node_type": "Pembibitan",
                "node_id": "1a",
                "node_codename": "cibubur-sayuranpagi_pembibitan_1a",
                "firmware_version": "1.0.0",
                "download_started_at": "2023-10-01T12:00:00+07:00",
                "firmware_size_kb": 1023.375,
                "bytes_written": 1047936,
                "download_speed_kbps": 20480.0,
                "download_completed_at": "2023-10-01T12:00:00+07:00",
                "flash_status": str(LogStatus.IN_PROGRESS)
            }
        }