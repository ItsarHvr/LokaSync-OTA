from fastapi import status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException

from externals.firebase.auth import verify_id_token
from cores.database import db, firmware_collection, log_collection

"""NOTES:
FIREBASE AUTH DOESN'T SUPPORT FOR ASYNC / AWAIT!
This dependency is synchronous and should be used in a synchronous context.
"""
security = HTTPBearer(auto_error=False)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency to get the current user from the request.
    This function verifies the Firebase ID token and returns the user information.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Not authenticated or invalid authentication scheme"
        )

    id_token = credentials.credentials
    return verify_id_token(id_token)

async def get_db_connection():
    """
    Dependency to get the database connection.
    This function can be used in FastAPI routes to access the database.
    """
    return db

async def get_firmware_collection():
    """
    Dependency to get the firmware collection.
    This function can be used in FastAPI routes to access the firmware collection.
    """
    return firmware_collection

async def get_log_collection():
    """
    Dependency to get the log collection.
    This function can be used in FastAPI routes to access the log collection.
    """
    return log_collection