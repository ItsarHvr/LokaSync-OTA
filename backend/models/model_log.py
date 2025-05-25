from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any, Dict, Optional

class Log(BaseModel):
    _id:str
    type:str
    message:str
    node_name:str
    timestamp:datetime
    firmware_version:str
    data: Optional[Dict[str, Any]] = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_custom_datetime(cls, v: Any) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v.replace(" ", " "), "%d %B %Y %H:%M:%S")
        return v