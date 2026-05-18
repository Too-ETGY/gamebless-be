from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime, timezone
from enum import Enum

class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    NONE = None

class UserProfile(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None
    avatar_url: Optional[str] = None


class AccountStats(BaseModel):
    total_points: int = 0
    current_streak: int = 0
    join_date: datetime = Field(default_factory=lambda: (datetime.now(timezone.utc)))