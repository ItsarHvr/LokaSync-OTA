from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
    UploadFile,
    Depends,
    Query,
    Path,
    Body,
    File
)
from typing import Optional, Dict, Any

from services.node import NodeService
from schemas.node import (
    NodeCreateSchema,
    NodeModifyVersionSchema,
    NodeResponse,
    SingleNodeResponse
)
from schemas.common import BaseAPIResponse
from cores.dependencies import get_current_user

node_router = APIRouter()

@node_router.post("/add-location", response_model=SingleNodeResponse)
async def add_node_location(
    request: Request,
    response: Response,
    payload: NodeCreateSchema = Body(...),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    node = await service.add_node_location(payload)
    return SingleNodeResponse(message="Node created", status_code=status.HTTP_201_CREATED, data=node)

@node_router.put("/edit/{node_codename}", response_model=SingleNodeResponse)
async def add_first_version(
    request: Request,
    response: Response,
    node_codename: str = Path(..., description="Node codename"),
    firmware_version: str = Body(...),
    firmware_url: Optional[str] = Body(None),
    firmware_file: Optional[UploadFile] = File(None),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    data = NodeModifyVersionSchema(
        firmware_version=firmware_version,
        firmware_url=firmware_url,
        firmware_file=firmware_file
    )
    node = await service.add_first_version(node_codename, data)
    return SingleNodeResponse(message="Firmware updated", status_code=status.HTTP_200_OK, data=node)

@node_router.post("/add-firmware/{node_codename}", response_model=SingleNodeResponse, status_code=status.HTTP_200_OK)
async def add_new_version(
    request: Request,
    response: Response,
    node_codename: str = Path(..., description="Node codename"),
    firmware_version: str = Body(...),
    firmware_url: Optional[str] = Body(None),
    firmware_file: Optional[UploadFile] = File(None),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    data = NodeModifyVersionSchema(
        firmware_version=firmware_version,
        firmware_url=firmware_url,
        firmware_file=firmware_file
    )
    node = await service.add_new_version(node_codename, data)
    return SingleNodeResponse(message="Firmware version updated", data=node)

@node_router.get("/", response_model=NodeResponse)
async def get_all_nodes(
    request: Request,
    response: Response,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
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
        message="Success",
        status_code=status.HTTP_200_OK,
        page=page,
        page_size=page_size,
        total_data=total,
        total_page=(total + page_size - 1) // page_size,
        filter_options=filter_options,
        data=nodes
    )

@node_router.get("/{node_codename}", response_model=SingleNodeResponse)
async def get_node(
    request: Request,
    response: Response,
    node_codename: str = Path(...),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    node = await service.get_node(node_codename)
    return SingleNodeResponse(message="Success", status_code=status.HTTP_200_OK, data=node)

@node_router.delete("/delete/{node_codename}", response_model=BaseAPIResponse)
async def delete_node(
    request: Request,
    response: Response,
    node_codename: str = Path(...),
    firmware_version: Optional[str] = Query(None),
    service: NodeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    await service.delete_node(node_codename, firmware_version)
    return BaseAPIResponse(message="Node deleted", status_code=status.HTTP_204_NO_CONTENT)