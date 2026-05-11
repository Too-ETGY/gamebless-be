from fastapi import Header
from typing import Optional
from app.core.security import verify_firebase_token
from app.core.exceptions import AppException

async def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """
    FastAPI dependency. Extracts and verifies Firebase JWT from
    Authorization header.

    Making it Optional here so FastAPI doesn't fire its own 422 —
    we handle missing/invalid headers ourselves for consistent response shape.
    """
    if not authorization:
        raise AppException(status_code=401, message="Authorization header is required")

    if not authorization.startswith("Bearer "):
        raise AppException(status_code=401, message="Invalid authorization header format. Use: Bearer <token>")

    token = authorization.removeprefix("Bearer ").strip()

    if not token:
        raise AppException(status_code=401, message="Token is missing")

    decoded = verify_firebase_token(token)
    return decoded