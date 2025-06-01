from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional

from dtos.dto_firmware import (
    UploadFirmwareForm, 
    UpdateFirmwareForm, 
    UpdateFirmwareDescriptionForm, 
    OutputFirmwarePagination, 
    OuputFirmwareByNodeName
)
from services.service_firmware import ServiceFirmware

router_firmware = APIRouter(prefix="/api/v1", tags=["Firmware"])

@router_firmware.get(
    "/firmware",
    response_model=OutputFirmwarePagination,
    summary="Get list of available firmwares."
)
async def get_list_firmware(
    node_id: Optional[int] = Query(default=None, ge=1),
    node_location: Optional[str] = Query(default=None, min_length=1, max_length=255),
    node_type: Optional[str] = Query(default=None, min_length=1, max_length=255),
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    service_firmware: ServiceFirmware = Depends()
):
    return await service_firmware.get_list_firmware(
        page=page,
        per_page=per_page,
        node_id=node_id,
        node_location=node_location,
        node_type=node_type
    )

@router_firmware.get(
    "/firmware/{node_codename}",
    response_model=OuputFirmwareByNodeName,
    summary="Get list firmware by node_codename."
)
async def get_by_node_name(
    node_codename: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    service_firmware: ServiceFirmware = Depends()
):
    response_get = await service_firmware.get_by_node_name(
        node_codename,
        page=page,
        per_page=per_page,
    )
    return response_get 

@router_firmware.post(
        "/firmware/add",
        summary="Add new firmware entry."
)
async def add_firmware(
    form: UploadFirmwareForm = Depends(),
    service_firmware: ServiceFirmware = Depends()
):
    try:
        await service_firmware.add_firmware(form)
        return JSONResponse(status_code=200, content={"message": "Add firmware successfully."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})    

@router_firmware.post(
        "/firmware/update/{node_name}",
        summary="Update firmware."
)
async def update_firmware(
    node_codename: str,
    form: UpdateFirmwareForm = Depends(),
    service_firmware: ServiceFirmware = Depends()
):
    try:
        await service_firmware.update_firmware(node_codename, form)
        return JSONResponse(status_code=200, content={"message": "Update firmware successfully."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router_firmware.put(
        "/firmware/update/firmware_description/",
        summary="Update firmware description."
)
async def update_firmware_description(
    node_codename: str = Query(...),
    firmware_version: str = Query(...),
    form: UpdateFirmwareDescriptionForm = Depends(),
    service_firmware: ServiceFirmware = Depends()
):
    try:
        await service_firmware.update_firmware_description(node_codename, firmware_version, form)
        return JSONResponse(status_code=200, content={"message": "Update firmware description successfully."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router_firmware.delete(
        "/firmware/delete/{node_codename}",
        summary="Delete firmware version or all firmware of a node."
)
async def delete_firmware(
    node_codename: str,
    firmware_version: Optional[str] = Query(None),
    service_firmware: ServiceFirmware = Depends()
):
    try:
        if firmware_version:
            await service_firmware.delete_by_firmware_version(node_codename, firmware_version)
            msg = f"Deleted firmware '{firmware_version}' from node '{node_codename}'"
        else:
            await service_firmware.delete_all_by_node_name(node_codename)
            msg = f"Deleted all firmwares from node '{node_codename}'"

        return JSONResponse(status_code=200, content={"message": msg})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
        