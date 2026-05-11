from typing import Any, Optional
from app.schemas.common import ApiResponse

def success_response(data: Any = None, message: str = "Success") -> ApiResponse:
    return ApiResponse(success=True, message=message, data=data)

def error_response(message: str, data: Any = None) -> ApiResponse:
    return ApiResponse(success=False, message=message, data=data)