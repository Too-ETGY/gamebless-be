from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse


# ── Requests ──────────────────────────────────────────────────────────────────

class DomainReportRequest(BaseModel):
    url: str                        # submitted by user, e.g. "bet-site.com"
    # reason: Optional[str] = None    # optional user note


# ── Response Data ─────────────────────────────────────────────────────────────

class DomainCheckData(BaseModel):
    url: str
    is_blocked: bool
    # status: Optional[str] = None    # "verified" | "pending_review" | "officially_blocked"
    reasoning: Optional[str] = None


class DomainReportData(BaseModel):
    url: str
    status: str                     # will be "pending_review" on submission
    message: str                    # e.g. "Report received, under review"


# ── Composed Responses ────────────────────────────────────────────────────────

DomainCheckResponse = ApiResponse[DomainCheckData]
DomainReportResponse = ApiResponse[DomainReportData]