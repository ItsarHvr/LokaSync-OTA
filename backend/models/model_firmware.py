from pydantic import BaseModel
from datetime import datetime


class Firmware(BaseModel):
    _id: str
    node_id: int
    node_location: str
    sensor_type: str
    node_name: str
    firmware_description: str
    firmware_version: str
    firmware_url: str
    latest_updated: datetime
