from fastapi import status
from fastapi.exceptions import HTTPException
from firebase_admin import auth

"""NOTES:
Use standard function to verify Firebase ID tokens.
Firebase auth does not support async operations directly,
so we use synchronous calls wrapped in a function.
"""

def verify_id_token(id_token: str) -> dict:
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            detail={
                "message": "Invalid ID token",
                "status_code": status.HTTP_401_UNAUTHORIZED
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            detail={
                "message": "ID token has expired",
                "status_code": status.HTTP_401_UNAUTHORIZED
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            detail={
                "message": "ID token has been revoked",
                "status_code": status.HTTP_401_UNAUTHORIZED
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        raise HTTPException(
            detail={
                "message": str(e),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )