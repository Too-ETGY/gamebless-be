from pydantic import BaseModel
from app.schemas.common import ApiResponse

# ── Requests ──────────────────────────────────────────────────────────────────
class DomainReportRequest(BaseModel):
    url: str                        # submitted by user, e.g. "bet-site.com"

# ── Response Data ─────────────────────────────────────────────────────────────
class DomainCheckData(BaseModel):
    url: str
    is_blocked: bool

class DomainReportData(BaseModel):
    url: str
    message: str = "Domain will be checked"

# ── Composed Responses ────────────────────────────────────────────────────────
DomainCheckResponse = ApiResponse[DomainCheckData]
DomainReportResponse = ApiResponse[DomainReportData]