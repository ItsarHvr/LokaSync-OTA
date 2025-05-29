from typing import List, Dict

from schemas.common import BaseAPIResponse

class ListNodeResponse(BaseAPIResponse):
    """
    List node schema for get available nodes.
    """
    data: Dict[str, List[str]]

    class Config:
        json_schema_extra = {
            "example": {
                "message": "List of nodes retrieved successfully",
                "status_code": 200,
                "data": {
                    "node_location": ["Cibubur-SayuranPagi", "Cibubur-SayuranSiang"],
                    "node_type": ["Penyemaian", "Pembibitan"],
                    "node_id": ["1a", "1b"]
                }
            }
        }