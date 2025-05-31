from fastapi import (
    APIRouter, 
    status,
    Response,
    Depends,
    Query
)
from typing import Optional, Dict, Any

from enums.log import LogStatus
from schemas.log import LogDataResponse
from services.log import LogService
from cores.dependencies import get_current_user
from utils.logger import logger

router_log = APIRouter()

@router_log.get(path="/", response_model=LogDataResponse)
async def get_all_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    node_location: Optional[str] = Query(default=None, min_length=3, max_length=255),
    node_type: Optional[str] = Query(default=None, min_length=3, max_length=255),
    flash_status: Optional[LogStatus] = Query(default=None, min_length=3, max_length=255),
    service: LogService = Depends(),
    current_user: dict = Depends(get_current_user)
) -> LogDataResponse:
    filters: Dict[str, Any] = {}

    if node_location:
        filters["node_location"] = node_location
    if node_type:
        filters["node_type"] = node_type
    if flash_status:
        filters["flash_status"] = flash_status

    logger.api_info(f"Retrieving logs - Page: {page}, Size: {page_size}, Filters: {filters} - User: {current_user.get('username', 'unknown')}")

    skip = (page - 1) * page_size
    total_data = await service.count_logs(filters)
    total_page = (total_data + page_size - 1) // page_size
    logs = await service.get_all_logs(filters=filters, skip=skip, limit=page_size)
    filter_options = await service.get_filter_options()
    
    logger.api_info(f"Successfully retrieved {len(logs)} logs out of {total_data} total - Page {page}/{total_page}")
    
    return LogDataResponse(
        message="List of logs retrieved successfully",
        status_code=status.HTTP_200_OK,
        page=page,
        page_size=page_size,
        total_data=total_data,
        total_page=total_page,
        filter_options=filter_options,
        data=logs
    )


@router_log.delete(
    path="/delete/{node_codename}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response
)
async def delete_log(
    node_codename: str,
    firmware_version: Optional[str] = None,
    service: LogService = Depends(),
    current_user: dict = Depends(get_current_user)
) -> None:
    logger.api_info(f"Deleting logs for node '{node_codename}' - Version: {firmware_version} - User: {current_user.get('username', 'unknown')}")
    
    await service.delete_log(node_codename, firmware_version)
    
    logger.api_info(f"Successfully deleted logs for node '{node_codename}' - Version: {firmware_version}")
    return Response(status_code=status.HTTP_204_NO_CONTENT, content=None)