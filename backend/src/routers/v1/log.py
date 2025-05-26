# from fastapi import APIRouter, Depends, Query
# from typing import Optional

# from dtos.dto_log import InputLog, OutputLogPagination
# from backend.services.log import ServiceLog

# router_log = APIRouter(prefix="/api/v1", tags=["Log"])

# @router_log.get(
#     "/log",
#     response_model=OutputLogPagination,
#     summary="Get list to the log"
# )
# async def get_list_log(
#     node_location: Optional[str] = Query(default=None, min_length=1, max_length=255),
#     node_status: Optional[bool] = Query(default=None, ge=1),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(5, ge=1, le=100),
#     service_log: ServiceLog = Depends()
# ):
#     response_get = await service_log.get_list_log(
#         page=page,
#         page_size=page_size,
#         node_location=node_location or None,
#         node_status=node_status or None
#     )
#     return response_get
