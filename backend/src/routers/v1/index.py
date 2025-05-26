# Redirect to the check health endpoint
from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse

from cores.config import env

router_index = APIRouter()
@router_index.get("/", include_in_schema=False, status_code=status.HTTP_302_FOUND)
async def redirect_to_health_check(request: Request):
    """
    Redirects to the health check endpoint.
    This is useful for checking the health of the API.
    """
    return RedirectResponse(
        url="/health",
        status_code=status.HTTP_302_FOUND
    )