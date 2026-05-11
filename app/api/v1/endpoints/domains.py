from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_user
from app.schemas.domain import DomainCheckResponse, DomainReportResponse, DomainReportRequest
from app.core.response import success_response

router = APIRouter()


@router.get("/check", response_model=DomainCheckResponse)
async def check_domain(
    url: str = Query(..., description="URL to check, e.g. bet-site.com"),
    current_user: dict = Depends(get_current_user),
):
    """
    Checks if a URL is in the blocked domain list.

    If blocked:
    - Increments today_access_try on user's daily progress
    - Resets current_streak on account_stats
    - Updates last_access_timestamp

    Flutter calls this when browser extension detects a URL.
    High-speed — Firestore document lookup by hashed domain ID.
    """
    # TODO: DomainService.check(url, uid)
    return success_response(data=None, message="Domain check endpoint ready")


@router.post("/report", response_model=DomainReportResponse)
async def report_domain(
    body: DomainReportRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    User submits a suspected gambling site.

    Flow:
    - Save domain with status "pending_review"
    - Trigger LLM analysis (Gemini) to verify and generate reasoning
    - Update status to "verified" or leave for manual review
    """
    # TODO: DomainService.report(body, uid)
    return success_response(data=None, message="Domain report endpoint ready")