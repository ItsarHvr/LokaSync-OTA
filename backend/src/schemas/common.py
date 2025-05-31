from pydantic import BaseModel
from typing import List


class BaseAPIResponse(BaseModel):
    """ Base class for API responses. """
    message: str
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "message": "Request was successful"
            }
        }


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
                "total_data": 0,
                "total_page": 1
            }
        }


class BaseFilterOptions(BaseModel):
    """ Base class for filter options. """
    node_locations: List[str]
    node_types: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "node_locations": ["Kebun Cibubur", "Kebun Bogor"],
                "node_types": ["Sayuran Pagi", "Buah Malam"],
            }
        }