from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any, Dict, Optional

class Log(BaseModel):
    _id:str
    type:str
    message:str
    node_id:str
    node_location:str
    node_type:str
    node_codename:str
    timestamp:datetime
    firmware_version:str
    node_mac:Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    firmware_size:Optional[float] = None
    download_speed:Optional[float] = None
    download_status:str
    ota_status:str

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_custom_datetime(cls, v: Any) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v.replace(" ", " "), "%d %B %Y %H:%M:%S")
        return v