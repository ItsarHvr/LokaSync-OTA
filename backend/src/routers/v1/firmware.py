from fastapi import APIRouter, Request, Response, Depends, Query
from typing import Optional

from schemas.firmware import (
    InputFirmware,
    UpdateFirmware,
    UpdateFirmwareDescription,
    OutputFirmwarePagination,
    OuputFirmwareByNodeName
)
from services.firmware import ServiceFirmware
from cores.dependencies import get_current_user
from cores.config import env
from middlewares.rate_limiter import limiter

router_firmware = APIRouter()

@router_firmware.get(
    path="/firmware",
    response_model=OutputFirmwarePagination,
    summary="Get list firmware"
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
async def get_list_firmware(
    request: Request,
    response: Response,
    node_id: Optional[int] = Query(default=None, ge=1),
    node_location: Optional[str] = Query(default=None, min_length=1, max_length=255),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    service_firmware: ServiceFirmware = Depends(),
    user: dict = Depends(get_current_user)
):
    return await service_firmware.get_list_firmware(
        page=page,
        page_size=page_size,
        node_id=node_id or None,
        node_location=node_location or None,
        user=user
    )

@router_firmware.get(
    path="/firmware/{node_name}",
    response_model=OuputFirmwareByNodeName,
    summary="Get list firmware version"
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
async def get_list_firmware_version(
    request: Request,
    response: Response,
    node_name: str,
    service_firmware: ServiceFirmware = Depends(),
    user: dict = Depends(get_current_user)
):
    return await service_firmware.get_list_firmware_version(
        node_name=node_name,
        user=user
    )

@router_firmware.post(
    path="/firmware/add",
    summary="Add new node"
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
async def add_new_node(
    request: Request,
    repsonse: Response,
    input_firmware: InputFirmware = Depends(),
    service_firmware: ServiceFirmware = Depends(),
    user: dict = Depends(get_current_user)
):
    return await service_firmware.add_new_node(input_firmware, user)

# Update firmware version of a specific node
@router_firmware.put(
    path="/firmware/update/{node_name}",
    summary="Update firmware version of a specific node"
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
async def update_firmware_version(
    request: Request,
    response: Response,
    node_name: str,
    update_firmware: UpdateFirmware = Depends(),
    service_firmware: ServiceFirmware = Depends(),
    user: dict = Depends(get_current_user)
):
    return await service_firmware.update_firmware_version(
        node_name,
        update_firmware,
        user
    )

# Update firmware description of a specific version
@router_firmware.put(
    path="/firmware/update/{node_name}/{firmware_version}",
    summary="Update firmware description of a specific version"
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
async def update_firmware_description(
    request: Request,
    response: Response,
    node_name: str,
    firmware_version: str,
    update_firmware: UpdateFirmwareDescription = Depends(),
    service_firmware: ServiceFirmware = Depends(),
    user: dict = Depends(get_current_user)
):
    return await service_firmware.update_firmware_description(
        node_name,
        firmware_version,
        update_firmware,
        user
    )

# Delete specific firmware version
@router_firmware.delete(
    path="/firmware/delete/{node_name}/{firmware_version}",
    summary="Delete specific firmware version by node name"
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
async def delete_firmware_version(
    request: Request,
    response: Response,
    node_name: str,
    firmware_version: str,
    service_firmware: ServiceFirmware = Depends(),
    user: dict = Depends(get_current_user)
):
    return await service_firmware.delete_firmware_version(
        node_name,
        firmware_version,
        user
    )

# Delete all firmware version
@router_firmware.delete(
    path="/firmware/delete/{node_name}",
    summary="Delete all firmware versions by node name"
)
@limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
async def delete_all_version(
    request: Request,
    response: Response,
    node_name: str,
    service_firmware: ServiceFirmware = Depends(),
    user: dict = Depends(get_current_user)
):
    return await service_firmware.delete_all_version(
        node_name,
        user
    )