# from pydantic import BaseModel, Field
# from typing import Optional, List, TypedDict

# from dtos.dto_common import BasePage
# from models.model_log import Log

# class InputLog(BaseModel):
#     node_location: str = Field(min_length=1, max_length=255)
#     node_status: bool = Field(default=False)
#     first_version: str = Field(min_length=1, max_length=255)
#     latest_version: str = Field(min_length=1, max_length=255)


#     class Config:
#         json_schema_extra ={
#             "example": {
#                 "node_location": "Depok Greenhouse",
#                 "node_status": True,
#                 "first_version": "1.0.0",
#                 "latest_version": "1.0.1",
#             }
#         }

# class FilterOption(TypedDict):
#     node_location: List[str]
#     node_status: List[bool]

# class OutputLogPagination(BasePage):
#     filter_options: FilterOption = Field(default_factory=lambda:{"node_location": [], "node_status": []})
#     log_data: List[Log] = Field(default_factory=list)
