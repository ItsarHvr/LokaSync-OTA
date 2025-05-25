from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi import HTTPException

from dtos.dto_log import InputLog, OutputLogPagination
from services.service_log import ServiceLog

router_log = APIRouter(prefix="/api/v1", tags=["Log"])

@router_log.get(
    "/log",
    response_model=OutputLogPagination,
    summary="Get list to the log"
)
async def get_list_log(
    node_name: Optional[str] = Query(default=None, min_length=1, max_length=255),
    firmware_version: Optional[str] = Query(default=None, ge=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    service_log: ServiceLog = Depends()
):
    try: 
        response_get = await service_log.get_list_log(
            page=page,
            per_page=per_page,
            node_name=node_name or None,
            firmware_version=firmware_version or None
        )
        return response_get
    except HTTPException as e:
        raise e
    except Exception as e:
        # Bisa log error dan lempar HTTPException 500
        raise HTTPException(status_code=500, detail=str(e))
