from pydantic import BaseModel
from typing import List

from enums.common import NodeLocation

class BasePagination(BaseModel):
    """ Base class for pagination. """
    page: int = 1
    page_size: int = 10
    total_data: int = 0
    total_page: int = 1

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "total_data": 100,
                "total_page": 10
            }
        }


class BaseFilterOptions(BaseModel):
    """ Base class for filter options. """
    node_id: List[int] = []
    node_location: List[str] = [loc.value for loc in NodeLocation]

    class Config:
        json_schema_extra = {
            "example": {
                "node_id": [i for i in range(1, 11)],
                "node_location": [loc.value for loc in NodeLocation]
            }
        }