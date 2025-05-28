from fastapi import APIRouter, status, Request, Response, Depends, Query
from fastapi.exceptions import HTTPException
from typing import Optional

# from schemas.firmware import (
#     InputNewNode,
#     UpdateFirmwareVersion,
#     UpdateFirmwareDescription,
#     OutputFirmwarePagination,
#     OuputFirmwareByNodeName
# )
# from services.firmware import ServiceFirmware

# from cores.dependencies import get_current_user
# from cores.config import env

# from middlewares.rate_limiter import limiter

firmware_router = APIRouter()


# @firmware_router.get("/", response_model=OutputFirmwarePagination)
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
# async def get_list_firmware(
#     request: Request,
#     response: Response,
#     node_id: Optional[int] = Query(None, ge=1),
#     node_location: Optional[str] = Query(None),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=50),
#     service_firmware: ServiceFirmware = Depends(),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get paginated firmware list with optional filters."""
#     if not current_user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

#     return await service_firmware.get_list_firmware(
#         node_id=node_id,
#         node_location=node_location,
#         page=page,
#         page_size=page_size,
#     )

# @firmware_router.post("/add")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
# async def add_new_node(
#     request: Request,
#     response: Response,
#     input_firmware: InputNewNode,
#     service_firmware: ServiceFirmware = Depends(),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Add new firmware node."""
#     if not current_user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

#     return await service_firmware.add_new_node(input_firmware)

# @firmware_router.get("/{node_name}", response_model=OuputFirmwareByNodeName)
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
# async def get_list_firmware_version(
#     request: Request,
#     response: Response,
#     node_name: str,
#     service_firmware: ServiceFirmware = Depends(),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get firmware versions for specific node."""
#     if not current_user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

#     return await service_firmware.get_list_firmware_version(node_name)

# @firmware_router.put("/update/{node_name}")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
# async def update_firmware_version(
#     request: Request,
#     response: Response,
#     node_name: str,
#     update_firmware: UpdateFirmwareVersion = Depends(UpdateFirmwareVersion.as_form),
#     service_firmware: ServiceFirmware = Depends(),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Update firmware version for a node."""
#     if not current_user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

#     return await service_firmware.update_firmware_version(node_name, update_firmware)

# @firmware_router.put("/update/{node_name}/{firmware_version}")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
# async def update_firmware_description(
#     request: Request,
#     response: Response,
#     node_name: str,
#     firmware_version: str,
#     update_firmware: UpdateFirmwareDescription,
#     service_firmware: ServiceFirmware = Depends(),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Update firmware description for specific version."""
#     if not current_user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

#     return await service_firmware.update_firmware_description(
#         node_name, firmware_version, update_firmware
#     )

# @firmware_router.delete("/delete/{node_name}/{firmware_version}")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
# async def delete_firmware_version(
#     request: Request,
#     response: Response,
#     node_name: str,
#     firmware_version: str,
#     service_firmware: ServiceFirmware = Depends(),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Delete specific firmware version."""
#     if not current_user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

#     return await service_firmware.delete_firmware_version(node_name, firmware_version)

# @firmware_router.delete("/delete/{node_name}")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute")
# @limiter.limit(f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour")
# async def delete_all_version(
#     request: Request,
#     response: Response,
#     node_name: str,
#     service_firmware: ServiceFirmware = Depends(),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Delete all firmware versions for a node."""
#     if not current_user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

#     return await service_firmware.delete_all_version(node_name)