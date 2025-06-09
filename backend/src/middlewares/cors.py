from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import List, Optional

from cores.config import env


# Custom CORS Middleware for LokaSync API
class CORSMiddleware(BaseHTTPMiddleware):
    def __init__(
      self, 
      app, 
      allowed_origins: Optional[List[str]] = None,
      allow_credentials: bool = False,
      allowed_methods: Optional[List[str]] = None,
      allowed_headers: Optional[List[str]] = None,
      expose_headers: Optional[List[str]] = None,
    ):
      super().__init__(app)
      self.allowed_origins: List[str] = allowed_origins
      self.allow_credentials: bool = allow_credentials
      self.allowed_methods: List[str] = allowed_methods
      self.allowed_headers: List[str] = allowed_headers
      self.expose_headers: List[str] = expose_headers

    def _is_origin_allowed(self, origin: str) -> bool:
      """Check if the origin is in the allowed origins list"""
      if "*" in self.allowed_origins:
        return True
      return origin in self.allowed_origins

    def _get_allowed_origin(self, request_origin: Optional[str]) -> str:
      """Get the appropriate allowed origin header value"""
      if "*" in self.allowed_origins:
        # If credentials are allowed, we can't use "*", must use specific origin
        if self.allow_credentials and request_origin and self._is_origin_allowed(request_origin):
          return request_origin
        elif not self.allow_credentials:
          return "*"

      # Check if the request origin is in allowed origins
      if request_origin and self._is_origin_allowed(request_origin):
        return request_origin

      # Default to the first allowed origin if none match
      return self.allowed_origins[0] if self.allowed_origins else "*"

    async def dispatch(self, request: Request, call_next):
      # Get the origin from the request
      request_origin = request.headers.get("origin")

      # Determine allowed origin for response
      allowed_origin = self._get_allowed_origin(request_origin)

      # Handle preflight requests (OPTIONS)
      if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = allowed_origin
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)

        if self.allow_credentials:
          response.headers["Access-Control-Allow-Credentials"] = "true"

        if self.expose_headers:
          response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        return response

      # Process the actual request
      response = await call_next(request)

      # Add CORS headers to all responses
      response.headers["Access-Control-Allow-Origin"] = allowed_origin
      response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
      response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)

      if self.allow_credentials:
        response.headers["Access-Control-Allow-Credentials"] = "true"

      if self.expose_headers:
        response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

      return response