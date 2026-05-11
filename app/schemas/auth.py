from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse


class Gender(str, Enum):
    MALE = "L"
    FEMALE = "P"
    NONE = None

# ── Requests ──────────────────────────────────────────────────────────────────

class SyncRequest(BaseModel):
    """
    Sent by frontend after Firebase login or when user updates their profile.
    Only username and email are required on first sync (from Google OAuth).
    Everything else is optional — user fills it in later from their profile page.
    """
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None     # Google profile picture
    birth_date: Optional[datetime] = None
    location: Optional[str] = None
    gender: Optional[Gender] = None         # "L" or "P"
    occupation: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    """For future PATCH /me endpoint — all fields optional."""
    full_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    location: Optional[str] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None


# ── Response Data ──────────────────────────────────────────────────────────────

class ProfileData(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[datetime] = None
    location: Optional[str] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None


class AccountStatsData(BaseModel):
    total_points: int = 0
    current_streak: int = 0
    highest_streak: int = 0
    last_access_timestamp: Optional[datetime] = None
    join_date: datetime


class UserData(BaseModel):
    uid: str
    profile: ProfileData
    account_stats: AccountStatsData

class UserProfileData(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[datetime] = None
    location: Optional[str] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None

# ── Composed Responses ─────────────────────────────────────────────────────────

SyncResponse = ApiResponse[UserData]
# MeResponse = ApiResponse[UserData]
ProgressResponse = ApiResponse[AccountStatsData]
ProfileResponse = ApiResponse[UserProfileData]