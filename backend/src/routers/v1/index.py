from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

router_index = APIRouter()

@router_index.get(path="/", include_in_schema=False, status_code=status.HTTP_302_FOUND)
async def redirect_to_health_check():
    """
    Redirects to the health check endpoint.
    This is useful for checking the health of the API.
    """
    return RedirectResponse(
        url="/health",
        status_code=status.HTTP_302_FOUND
    )