from pydantic import BaseModel, EmailStr
from app.schemas.common import ApiResponse
from app.schemas.user import ProfileData, AccountStatsData

# ── Requests ──────────────────────────────────────────────────────────────────

class SyncRequest(BaseModel):
    email: EmailStr
    # avatar_url: str | None = None       # from Google OAuth


# ── Response Data ─────────────────────────────────────────────────────────────

class SyncData(BaseModel):
    is_new_user: bool
    profile : ProfileData
    account_stats : AccountStatsData


# ── Composed Responses ────────────────────────────────────────────────────────

SyncResponse = ApiResponse[SyncData]