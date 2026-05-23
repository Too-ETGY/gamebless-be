from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from app.models.challenge import ChallengeType

class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    NONE = None

# document ID uid: str
class UserProfile(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    occupation: Optional[str] = None
    join_date: datetime = Field(default_factory=lambda: (datetime.now(timezone.utc)))
    
# users/{uid}/completed_challenges/{task_id}
class CompletedChallenges(BaseModel) :
    type: ChallengeType
    points: int
    completed_at: datetime = Field(default_factory=lambda: (datetime.now(timezone.utc)))