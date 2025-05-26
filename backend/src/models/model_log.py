# from pydantic import BaseModel, field_validator
# from datetime import datetime
# from typing import Any

# class Log(BaseModel):
#     _id:str
#     node_location:str
#     node_status:bool
#     latest_updated:datetime
#     first_version:str
#     latest_version:str

#     @field_validator("latest_updated", mode="before")
#     @classmethod
#     def parse_custom_datetime(cls, v: Any) -> datetime:
#         if isinstance(v, str):
#             return datetime.strptime(v.replace(" ", " "), "%d %B %Y %H:%M:%S")
#         return v