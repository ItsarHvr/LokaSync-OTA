# from fastapi import Depends
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import HTTPException
# from firebase_admin import firestore
# from typing import Optional
# from datetime import datetime
# from math import ceil

# from google.cloud.firestore_v1.base_query import FieldFilter
# from dtos.dto_log import InputLog, OutputLogPagination
# from backend.repositories.log import LogRepository
# from models.model_log import Log

# class ServiceLog:
#     def __init__(self, log_repository: LogRepository = Depends()):
#         self.db = firestore.client().collection("log")
#         self.counter_ref = firestore.client().collection("counters").document("log_counter")
#         self.log_repository = log_repository

#     async def get_list_log(
#         self,
#         node_location: Optional[str] = None,
#         node_status: Optional[bool] = None,
#         page: int = 1,
#         page_size: int = 5
#     ) -> OutputLogPagination | dict:
#         try:
#             # 1. Data firmware
#             list_log: list = await self.log_repository.get_list_log(
#                 page=page,
#                 page_size=page_size,
#                 node_location=node_location,
#                 node_status=node_status
#             )

#             # 2. Total data
#             total_data: int = await self.log_repository.count_list_log(
#                 node_location=node_location,
#                 node_status=node_status
#             )

#             # 3. Total page
#             total_page: int = ceil(total_data / page_size) if total_data else 1

#             # 4. Get filter options
#             filter_options: dict = await self.log_repository.get_filter_options()

#             # 5. Return response
#             return OutputLogPagination(
#                 page=page,
#                 page_size=page_size,
#                 total_data=total_data,
#                 total_page=total_page,
#                 filter_options=filter_options,
#                 log_data=list_log
#             )
#         except Exception as e:
#             return HTTPException(status_code=500, detail=str(e))