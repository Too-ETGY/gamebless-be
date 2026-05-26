from fastapi import APIRouter, Depends, Query, BackgroundTasks
from app.db.firebase import get_firestore
from app.db.repositories.domain_repo import DomainRepository
from app.services.domain_service import check_domain, report_domain
from app.utils.limiter import RateLimiter
from app.schemas.domain import (
    DomainCheckResponse,
    DomainReportResponse,
    DomainCheckData,
    DomainReportData,
    DomainReportRequest,
)
from app.core.response import success_response

router = APIRouter()


def get_domain_repo() -> DomainRepository:
    db = get_firestore()
    return DomainRepository(db)


@router.get("/check", response_model=DomainCheckResponse, dependencies=[Depends(RateLimiter(limit=60, window=60, key_type="ip"))])
async def check_domain_endpoint(
    url: str = Query(..., description="URL to check e.g. bet-site.com"),
    repo: DomainRepository = Depends(get_domain_repo),
):
    """
    Checks if a URL is blocked.

    1. Exact Firestore match  → blocked
    2. Vector similarity ≥ 0.90 → blocked + saved
    3. Otherwise              → not blocked

    No auth required. No scraping — must be fast.
    """
    is_blocked = await check_domain(url, repo)
    return success_response(
        data=DomainCheckData(url=url, is_blocked=is_blocked),
        message="Domain checked successfully",
    )


@router.post("/report", response_model=DomainReportResponse)
async def report_domain_endpoint(
    body: DomainReportRequest,
    background_tasks: BackgroundTasks,
    repo: DomainRepository = Depends(get_domain_repo),
):
    """
    User reports a suspected gambling site.

    Returns immediately. Analysis runs in the background:
    1. Already in Firestore?          → skip
    2. Vector similarity ≥ 0.85?      → save with similarity reasoning
    3. Otherwise                      → scrape + LLM analysis → save if blocked
    """
    background_tasks.add_task(report_domain, body.url, repo)
    return success_response(
        data=DomainReportData(url=body.url),
        message="Report received, domain will be analyzed",
    )