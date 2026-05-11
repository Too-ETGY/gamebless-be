from pydantic import BaseModel
from typing import Optional, List


class UserProgress(BaseModel):
    date: str                               # document ID format: "YYYY-MM-DD"
    completed_challenges: List[str] = []    # array of task_ids
    today_points_earned: int = 0
    streak_maintained: Optional[bool] = None
    ai_summary: Optional[str] = None
    today_access_try: int = 0