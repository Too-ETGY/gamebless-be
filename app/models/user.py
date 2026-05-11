from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone, timezone
from enum import Enum

class Gender(str, Enum):
    MALE = "L"
    FEMALE = "P"
    NONE = None

class UserProfile(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    location: Optional[str] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None
    avatar_url: Optional[str] = None     # pulled from Google OAuth on first sync


class AccountStats(BaseModel):
    total_points: int = 0
    current_streak: int = 0
    highest_streak: int = 0
    last_access_timestamp: Optional[datetime] = None
    join_date: datetime = Field(default_factory=lambda: (datetime.now(timezone.utc)))