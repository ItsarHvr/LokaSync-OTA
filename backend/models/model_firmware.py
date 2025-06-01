from pydantic import BaseModel
from datetime import datetime


class Firmware(BaseModel):
    _id: str
    node_id: str
    node_location: str
    node_type: str
    node_codename: str
    firmware_description: str
    firmware_version: str
    firmware_url: str
    latest_updated: datetime
    is_group: bool
