from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List
from challenge import ChallengeType

# document ID format: "YYYY-MM-DD"

class UserProgress(BaseModel):
    completed_challenges: List[str] = Field(default_factory=list)    # array of task_ids
    challenges_by_type: dict[ChallengeType, int] = Field(default_factory=dict)  # e.g. {"video": 4, "article": 2, "funfact": 1}
    access_attempts_count: int = 0      # attempts means: user is accessing a judol site
    streak_maintained: bool = True      # False if access_attempts_count > 0
    updated_at: datetime = Field(default_factory=lambda: (datetime.now(timezone.utc)))  