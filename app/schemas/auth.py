from pydantic import BaseModel, EmailStr
from app.schemas.common import ApiResponse
from app.schemas.user import ProfileData

# ── Requests ──────────────────────────────────────────────────────────────────

class SyncRequest(BaseModel):
    email: EmailStr
    # avatar_url: str | None = None       # from Google OAuth


# ── Response Data ─────────────────────────────────────────────────────────────

class SyncData(BaseModel):
    is_new_user: bool
    profile : ProfileData

# ── Composed Responses ────────────────────────────────────────────────────────

SyncResponse = ApiResponse[SyncData]