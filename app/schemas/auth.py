from pydantic import BaseModel, EmailStr
from app.schemas.common import ApiResponse


# ── Requests ──────────────────────────────────────────────────────────────────

class SyncRequest(BaseModel):
    email: EmailStr
    avatar_url: str | None = None       # from Google OAuth


# ── Response Data ─────────────────────────────────────────────────────────────

class SyncData(BaseModel):
    uid: str
    email: EmailStr
    is_new_user: bool


# ── Composed Responses ────────────────────────────────────────────────────────

SyncResponse = ApiResponse[SyncData]