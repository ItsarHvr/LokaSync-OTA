from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from cores.config import env

router_health = APIRouter()

@router_health.get(path="/health", include_in_schema=False, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    Returns a simple JSON response indicating the service is healthy.
    """
    try:
        return JSONResponse(
            content={
                "message": "healthy",
                "status_code": status.HTTP_200_OK,
                "api_docs": {
                    "swagger": f"/api/v{env.APP_VERSION}/docs",
                    "redoc": f"/api/v{env.APP_VERSION}/redoc",
                }
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )