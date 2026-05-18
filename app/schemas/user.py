from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from app.models.user import Gender
from app.schemas.common import ApiResponse


# ── Requests ──────────────────────────────────────────────────────────────────

class SyncRequest(BaseModel):
    """POST /auth/sync — called by Firebase on first login. Creates user document."""
    email: EmailStr
    avatar_url: Optional[str] = None    # from Google OAuth


class UpdateProfileRequest(BaseModel):
    """PUT /users/me — user fills in their profile."""
    username: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None
    avatar_url: Optional[str] = None


# ── Response Data ─────────────────────────────────────────────────────────────

class ProfileData(BaseModel):
    uid: str
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None
    avatar_url: Optional[str] = None


class AccountStatsData(BaseModel):
    total_points: int
    current_streak: int
    join_date: datetime


class MeData(BaseModel):
    """Full snapshot — profile + stats. Used by GET /users/me."""
    profile: ProfileData
    account_stats: AccountStatsData


# ── Composed Responses ────────────────────────────────────────────────────────

SyncResponse = ApiResponse[ProfileData]
MeResponse = ApiResponse[MeData]
UpdateProfileResponse = ApiResponse[ProfileData]


class AttemptRequest(BaseModel):
    """POST /users/attempts — frontend calls this when /check returns is_blocked=true."""
    url: str