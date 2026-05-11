from fastapi import APIRouter
from app.schemas.common import ApiResponse
from app.core.response import success_response

router = APIRouter()

@router.get("/health", response_model=ApiResponse)
async def health_check():
    return success_response(
        data=None,
        message="Service is healthy"
    )