from fastapi import (
    APIRouter, 
    status,
    Response,
    Depends,
    Query,
    Path,
)
from typing import Optional, Dict, Any

from fastapi.responses import StreamingResponse

from enums.log import LogStatus
from schemas.log import LogDataResponse, SingleLogResponse
from services.log import LogService
from cores.dependencies import get_current_user
from utils.datetime import get_current_datetime
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

    logger.api_info(f"Retrieving logs - Page: {page}, Size: {page_size}, Filters: {filters}")

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

@router_log.get(
    path="/detail/{session_id}",
    response_model=SingleLogResponse
)
async def get_detail_log(
    session_id: str = Path(..., max_length=15),
    service: LogService = Depends(),
    current_user: dict = Depends(get_current_user)
) -> SingleLogResponse:
    logger.api_info(f"Retrieving log details for session id '{session_id}'")

    log = await service.get_detail_log(session_id=session_id)

    if log:
        logger.api_info(f"Successfully retrieved log details for session id '{session_id}'")
    else:
        logger.api_error(f"No log found for session id '{session_id}'")

    return SingleLogResponse(
        message="Log details retrieved successfully",
        status_code=status.HTTP_200_OK,
        data=log
    )

@router_log.delete(
    path="/delete/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response
)
async def delete_log(
    session_id: str = Path(..., max_length=15),
    service: LogService = Depends(),
    current_user: dict = Depends(get_current_user)
) -> None:
    logger.api_info(f"Deleting logs for session id '{session_id}'")

    await service.delete_log(session_id)

    logger.api_info(f"Successfully deleted logs for session id '{session_id}'")
    return Response(status_code=status.HTTP_204_NO_CONTENT, content=None)

@router_log.get(
    path="/export",
    response_class=StreamingResponse
)
async def export_logs(
    type: str = Query(default="csv", regex="^(csv|pdf)$"),
    auto_gen_fname: bool = Query(default=True),
    filename: Optional[str] = Query(default="lokasync_logs"),
    with_datetime: bool = Query(default=False),
    node_location: Optional[str] = Query(default=None, min_length=3, max_length=255),
    node_type: Optional[str] = Query(default=None, min_length=3, max_length=255),
    flash_status: Optional[LogStatus] = Query(default=None),
    service: LogService = Depends(),
    current_user: dict = Depends(get_current_user)
) -> StreamingResponse:
    """
    Export logs to CSV or PDF format.
    Optional filters can be applied.
    """
    logger.api_info(f"Exporting logs to {type.upper()} format")
    
    # Apply any filters provided
    filters = {}
    if node_location:
        filters["node_location"] = node_location
    if node_type:
        filters["node_type"] = node_type
    if flash_status:
        filters["flash_status"] = flash_status
    
    # Generate the file
    export_data = await service.export_logs(export_type=type, filters=filters)
    
    # Generate filename based on parameters
    if auto_gen_fname:
        base_filename = "lokasync_logs"
        if with_datetime:
            date_str = get_current_datetime().strftime("%Y-%m-%d")
            final_filename = f"{base_filename}_{date_str}.{type}"
        else:
            final_filename = f"{base_filename}.{type}"
    else:
        # Use provided filename
        if with_datetime:
            date_str = get_current_datetime().strftime("%Y-%m-%d")
            # Remove extension if provided, then add date and extension
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            final_filename = f"{base_name}_{date_str}.{type}"
        else:
            # Ensure proper extension
            if not filename.endswith(f".{type}"):
                final_filename = f"{filename}.{type}"
            else:
                final_filename = filename
    
    # Return as streaming response
    content_types = {
        "csv": "text/csv",
        "pdf": "application/pdf"
    }
    
    logger.api_info(f"Successfully exported logs to '{final_filename}.{type}'")
    
    return StreamingResponse(
        export_data,
        media_type=content_types[type],
        headers={
            "Content-Disposition": f"attachment; filename={final_filename}"
        }
    )