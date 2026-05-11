from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from app.schemas.common import ApiResponse


# ── Response Data ─────────────────────────────────────────────────────────────

class ChallengeTask(BaseModel):
    task_id: str
    type: str                       # "video" | "article" | "exercise"
    content_url: str
    point_value: int
    description: str


class DailyChallengesData(BaseModel):
    date: str                       # "YYYY-MM-DD"
    tasks: List[ChallengeTask]


class AllChallengesData(BaseModel):
    challenges: List[DailyChallengesData]


class CompleteTaskData(BaseModel):
    task_id: str
    points_awarded: int
    total_points: int               # updated total after awarding


# ── Composed Responses ────────────────────────────────────────────────────────

DailyChallengesResponse = ApiResponse[DailyChallengesData]
AllChallengesResponse = ApiResponse[AllChallengesData]
CompleteTaskResponse = ApiResponse[CompleteTaskData]