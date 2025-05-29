from fastapi import APIRouter, Depends, Query, Request, Response

from schemas.monitoring import ListNodeResponse
from services.monitoring import MonitoringService
from middlewares.rate_limiter import limiter
from cores.dependencies import get_current_user
from cores.config import env

router_monitoring = APIRouter()

@router_monitoring.get(
    "/",
    response_model=ListNodeResponse,
    description="Get a list of unique node locations, types, and IDs",
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def get_list_nodes(
    request: Request,
    response: Response,
    service: MonitoringService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a list of unique node locations, types, and IDs from the database.
    """
    result = await service.get_list_nodes()

    return ListNodeResponse(
        message="List of nodes retrieved successfully",
        status_code=200,
        data=result
    )