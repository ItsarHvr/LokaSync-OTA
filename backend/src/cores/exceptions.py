from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract the first error message, or fallback
    first_error = exc.errors()[0] if exc.errors() else {}
    msg = first_error.get("msg", "Invalid input.")

    # Remove "Value error, " prefix if present
    if msg.startswith("Value error, "):
        msg = msg.replace("Value error, ", "", 1)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": msg, "status_code": 422},
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    # Use exc.detail as message, or fallback
    msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={"message": msg, "status_code": exc.status_code},
    )