from fastapi import status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException

from externals.firebase.auth import verify_id_token
from cores.database import _db

"""NOTES:
FIREBASE AUTH DOESN'T SUPPORT FOR ASYNC / AWAIT!
This dependency is synchronous and should be used in a synchronous context.
"""
security = HTTPBearer(auto_error=False)
def get_current_user(
    id_token: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency to get the current user from the request.
    This function verifies the Firebase ID token and returns the user information.
    """
    if id_token is None or id_token.scheme.lower() != "bearer":
        raise HTTPException(
            detail="Invalid or missing authorization token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return verify_id_token(id_token.credentials)

async def get_db_connection():
    """
    Dependency to get the database connection.
    This function can be used in FastAPI routes to access the database.
    """
    return _db

async def get_nodes_collection():
    """
    Dependency to get the nodes collection.
    This function can be used in FastAPI routes to access the nodes collection.
    """
    return _db.get_collection("nodes")

async def get_logs_collection():
    """
    Dependency to get the log collection.
    This function can be used in FastAPI routes to access the log collection.
    """
    return _db.get_collection("logs")