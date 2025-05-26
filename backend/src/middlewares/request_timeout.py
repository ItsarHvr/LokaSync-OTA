import asyncio
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from cores.config import env

class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout_seconds: float = env.MIDDLEWARE_REQUEST_TIMEOUT_SECOND):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    def get_timeout_for_path(self, path: str) -> float:
        if any(endpoint in path for endpoint in ["/firmware/add", "/firmware/update"]):
            return env.MIDDLEWARE_REQUEST_TIMEOUT_SECOND_UPLOAD
        if path.startswith("/api"):
            return env.MIDDLEWARE_REQUEST_TIMEOUT_SECOND
        if "/health" in path:
            return 10.0
        return self.timeout_seconds

    async def dispatch(self, request: Request, call_next):
        timeout = self.get_timeout_for_path(request.url.path)
        try:
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail={
                    "error": "Request timed out.",
                    "message": f"Request took longer than {timeout} seconds to complete.",
                    "path": str(request.url.path)
                }
            )
        except asyncio.CancelledError:
            # Don't raise anything new; let ASGI handle task cancellation
            raise
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail={
        #             "error": "Internal Server Error",
        #             "message": f"An unexpected error occurred: {str(e)}",
        #             "path": str(request.url.path)
        #         }
        #     )