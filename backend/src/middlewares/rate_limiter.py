from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from cores.config import env


def get_client_ip(request: Request) -> str:
    """
    Get client IP address, handling common proxy headers.
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()
        
    # Fallback to remote address from connection, or localhost if not available
    return get_remote_address(request) or "127.0.0.1" or "localhost"

limiter = Limiter(
    key_func=get_client_ip,
    storage_uri="memory://",
    # default_limits=[
    #     f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_MINUTE}/minute",
    #     f"{env.MIDDLEWARE_RATE_LIMIT_REQUEST_PER_HOUR}/hour"
    # ]
)

def init_rate_limiter(app: FastAPI):
    """
    Initialize the rate limiter middleware for the FastAPI application.
    This function sets up the rate limiting configuration and error handling.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)