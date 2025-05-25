from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from typing import Optional
from datetime import datetime
from math import ceil
from databases.mongodb import get_log_collection

from dtos.dto_log import InputLog, OutputLogPagination
from repositories.repository_log import LogRepository
from models.model_log import Log

def get_log_repository():
    collection = get_log_collection()
    return LogRepository(collection)

class ServiceLog:
    def __init__(self, log_repository: LogRepository = Depends(get_log_repository)):
        self.log_repository = log_repository

    async def get_list_log(
        self,
        node_name: Optional[str] = None,
        firmware_version: Optional[str] = None,
        page: int = 1,
        per_page: int = 5
    ) -> OutputLogPagination:
        try:
            # 1. Data firmware
            list_log: list = await self.log_repository.get_list_log(
                page=page,
                per_page=per_page,
                node_name=node_name,
                firmware_version=firmware_version
            )

            # 2. Total data
            total_data: int = await self.log_repository.count_list_log(
                node_name=node_name,
                firmware_version=firmware_version
            )

            # 3. Total page
            total_page: int = ceil(total_data / per_page) if total_data else 1

            # 4. Get filter options
            filter_options = await self.log_repository.get_filter_options()

            # 5. Return response
            return OutputLogPagination(
                page=page,
                per_page=per_page,
                total_data=total_data,
                total_page=total_page,
                filter_options=filter_options,
                log_data=list_log
            )
        except Exception as e:
            print("Error di get_list_log:", e)
            raise HTTPException(status_code=500, detail=str(e))