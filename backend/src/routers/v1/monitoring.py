from fastapi import (
    APIRouter,
    status,
    Depends
)

from schemas.monitoring import ListNodeResponse
from services.monitoring import MonitoringService
from cores.dependencies import get_current_user
from utils.logger import logger

router_monitoring = APIRouter()

@router_monitoring.get(path="/", response_model=ListNodeResponse)
async def get_list_nodes(
    service: MonitoringService = Depends(),
    current_user: dict = Depends(get_current_user)
) -> ListNodeResponse:
    logger.api_info(f"Getting list of available nodes")
    
    nodes = await service.get_list_nodes()
    
    total_items = sum(len(v) for v in nodes.values() if isinstance(v, list))
    logger.api_info(f"Successfully retrieved {total_items} total distinct node values")

    return ListNodeResponse(
        message="List of nodes retrieved successfully",
        status_code=status.HTTP_200_OK,
        data=nodes
    )