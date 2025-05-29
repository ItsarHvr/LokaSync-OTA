from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
    Depends,
    Query,
    Path,
    Body
)
from typing import Optional, Dict, Any

from services.node import NodeService
from schemas.node import (
    NodeCreateSchema,
    NodeModifyVersionSchema,
    NodeResponse,
    SingleNodeResponse,
    FirmwareVersionListResponse
)
from schemas.common import BaseAPIResponse
from cores.dependencies import get_current_user
from middlewares.rate_limiter import limiter
from cores.config import env

router_node = APIRouter()

@router_node.post("/add-location", response_model=SingleNodeResponse)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def add_node_location(
    request: Request,
    response: Response,
    payload: NodeCreateSchema = Body(...),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    node = await service.add_node_location(payload)
    return SingleNodeResponse(
        message="Node created",
        status_code=status.HTTP_201_CREATED,
        data=node
    )

@router_node.post("/add-firmware/{node_codename}", response_model=SingleNodeResponse)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def upsert_firmware(
    request: Request,
    response: Response,
    node_codename: str = Path(..., description="Node codename"),
    payload: NodeModifyVersionSchema = Body(...),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    node = await service.upsert_firmware(node_codename, payload)
    return SingleNodeResponse(
        message="Firmware version added",
        status_code=status.HTTP_200_OK,
        data=node
    )

@router_node.patch("/edit-firmware/{node_codename}", response_model=SingleNodeResponse)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def edit_description(
    request: Request,
    response: Response,
    node_codename: str = Path(..., description="Node codename to edit "),
    firmware_version: Optional[str] = Query(None, description="Firmware version to edit"),
    description: Optional[str] = Body(None, embed=True),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    node = await service.update_description(node_codename, description, firmware_version)
    return SingleNodeResponse(
        message="Description updated",
        status_code=status.HTTP_200_OK,
        data=node
    )

@router_node.get("/", response_model=NodeResponse)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def get_all_nodes(
    request: Request,
    response: Response,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    node_location: Optional[str] = Query(None),
    node_type: Optional[str] = Query(None),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    filters: Dict[str, Any] = {}
    if node_location:
        filters["node_location"] = node_location
    if node_type:
        filters["node_type"] = node_type

    skip = (page - 1) * page_size
    nodes = await service.get_all_nodes(filters, skip, page_size)
    total = await service.count_nodes(filters)
    filter_options = await service.get_filter_options()

    return NodeResponse(
        message="Success get all nodes",
        status_code=status.HTTP_200_OK,
        page=page,
        page_size=page_size,
        total_data=total,
        total_page=(total + page_size - 1) // page_size,
        filter_options=filter_options,
        data=nodes
    )

@router_node.get("/detail/{node_codename}", response_model=SingleNodeResponse)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def get_detail_node(
    request: Request,
    response: Response,
    node_codename: str = Path(..., description="Node codename to get details"),
    firmware_version: Optional[str] = Query(None, description="Firmware version to get details"),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    node = await service.get_detail_node(node_codename, firmware_version)
    return SingleNodeResponse(
        message="Success get detail node",
        status_code=status.HTTP_200_OK,
        data=node
    )

@router_node.get("/version/{node_codename}", response_model=FirmwareVersionListResponse)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def get_firmware_versions(
    request: Request,
    response: Response,
    node_codename: str = Path(..., description="Node codename"),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    versions = await service.get_firmware_versions(node_codename)
    return FirmwareVersionListResponse(
        message="Success get firmware versions",
        status_code=status.HTTP_200_OK,
        data=versions
    )

@router_node.delete("/delete/{node_codename}", response_model=BaseAPIResponse)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
async def delete_node(
    request: Request,
    response: Response,
    node_codename: str = Path(..., max_length=255, description="Node codename to delete"),
    firmware_version: Optional[str] = Query(None, max_length=255, description="Firmware version to delete"),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    await service.delete_node(node_codename, firmware_version)
    return BaseAPIResponse(message="Node deleted", status_code=status.HTTP_204_NO_CONTENT)