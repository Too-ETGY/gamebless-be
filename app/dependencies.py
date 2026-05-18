from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.security import verify_firebase_token
from app.core.exceptions import AppException

# 1. Instantiate the security scheme. 
# auto_error=False keeps FastAPI from auto-throwing its own 422/401 
# so you can maintain your custom response shape.
security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> dict:
    """
    FastAPI dependency. Extracts and verifies Firebase JWT from
    Authorization header using FastAPI's native HTTPBearer wrapper.
    """
    # If credentials is None, it means the Authorization header was missing completely
    if not credentials:
        raise AppException(status_code=401, message="Authorization header is required")

    # FastAPI's HTTPBearer handles the "Bearer " prefix stripping for us.
    # credentials.credentials contains just the raw JWT token string.
    token = credentials.credentials.strip()

    if not token:
        raise AppException(status_code=401, message="Token is missing")

    decoded = verify_firebase_token(token)
    return decoded