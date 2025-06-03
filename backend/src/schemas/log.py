from typing import List, Optional

from schemas.common import (
    BaseAPIResponse,
    BasePagination,
    BaseFilterOptions
)
from models.log import LogModel
from enums.log import LogStatus


class LogFilterOptions(BaseFilterOptions):
    """ Filter options specific to logs data. """
    flash_statuses: List[LogStatus]


class SingleLogResponse(BaseAPIResponse):
    """ Response schema for a single log entry. """
    data: Optional[LogModel] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Log retrieved successfully",
                "status_code": 200,
                "data": {
                    "_id": "60c72b2f9b1e8d001c8e4f3a",
                    "created_at": "2023-10-01T12:00:00Z",
                    "session_id": "session123",
                    "node_mac": "00:1A:2B:3C:4D:5E",
                    "node_location": "Cibubur-SayuranPagi",
                    "node_type": "Pembibitan",
                    "node_id": "1a",
                    "node_codename": "cibubur-sayuranpagi_pembibitan_1a",
                    "firmware_version": "1.0.0",
                    "download_started_at": None,
                    "firmware_size_kb": None,
                    "bytes_written": None,
                    "download_duration_sec": None,
                    "download_speed_kbps": None,
                    "download_completed_at": None,
                    "flash_completed_at": None,
                    "flash_status": str(LogStatus.IN_PROGRESS)
                }
            }
        }


class LogDataResponse(BaseAPIResponse, BasePagination):
    filter_options: LogFilterOptions = {}
    data: List[LogModel] = []

    class Config:
        json_schema_extra = {
            "example": {
                "message": "List of logs retrieved successfully",
                "status_code": 200,
                "page": 1,
                "page_size": 10,
                "total_data": 0,
                "total_page": 1,
                "filter_options": {
                    "node_locations": [
                        "Cibubur-SayuranPagi",
                        "Bogor-SayuranPagi"
                    ],
                    "node_types": [
                        "Penyemaian",
                        "Pembibitan"
                    ],
                    "flash_statuses": [
                        LogStatus.IN_PROGRESS,
                        LogStatus.SUCCESS,
                        LogStatus.FAILED
                    ]
                },
                "data": [
                    {
                        "_id": "60c72b2f9b1e8d001c8e4f3a",
                        "created_at": "2023-10-01T12:00:00Z",
                        "session_id": "session123",
                        "node_mac": "00:1A:2B:3C:4D:5E",
                        "node_location": "Cibubur-SayuranPagi",
                        "node_type": "Pembibitan",
                        "node_id": "1a",
                        "node_codename": "cibubur-sayuranpagi_pembibitan_1a",
                        "firmware_version": "1.0.0",
                        "download_started_at": None,
                        "firmware_size_kb": None,
                        "bytes_written": None,
                        "download_duration_sec": None,
                        "download_speed_kbps": None,
                        "download_completed_at": None,
                        "flash_completed_at": None,
                        "flash_status": str(LogStatus.IN_PROGRESS)
                    }
                ]
            }
        }