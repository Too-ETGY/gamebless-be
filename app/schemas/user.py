from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import Gender, UserProfile
from app.schemas.common import ApiResponse


# ── Requests ──────────────────────────────────────────────────────────────────

class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None


# ── Response Data ─────────────────────────────────────────────────────────────

class ProfileData(UserProfile):
    uid: str

class AccountStatsData(BaseModel):
    total_points: int
    current_streak: int
    days_since_joined: int


class MeData(BaseModel):
    profile: ProfileData
    account_stats: AccountStatsData


# ── Composed Responses ────────────────────────────────────────────────────────

MeResponse = ApiResponse[MeData]
UpdateProfileResponse = ApiResponse[ProfileData]


class AttemptRequest(BaseModel):
    """POST /users/attempts — frontend calls this when /check returns is_blocked=true."""
    url: Optional[str] = None