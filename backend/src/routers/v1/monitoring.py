from fastapi import (
    APIRouter,
    status,
    Depends
)

from schemas.monitoring import ListNodeResponse
from services.monitoring import MonitoringService
from cores.dependencies import get_current_user

router_monitoring = APIRouter()

@router_monitoring.get(path="/", response_model=ListNodeResponse)
async def get_list_nodes(
    service: MonitoringService = Depends(),
    current_user: dict = Depends(get_current_user)
) -> ListNodeResponse:
    nodes = await service.get_list_nodes()

    return ListNodeResponse(
        message="List of nodes retrieved successfully",
        status_code=status.HTTP_200_OK,
        data=nodes
    )