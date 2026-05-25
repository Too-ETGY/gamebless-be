from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.challenge import ChallengeType, ChallengeTask
from app.schemas.common import ApiResponse


# ── Response Data ─────────────────────────────────────────────────────────────

class ChallengeTaskData(ChallengeTask):
    task_id: str
    is_completed: bool = False


class AllChallengesData(BaseModel):
    challenges: List[ChallengeTaskData]
    total: int


class CompleteChallengeData(BaseModel):
    task_id: str
    points_awarded: int
    total_points: int


class CompletedChallengeData(BaseModel):
    """Lightweight — option B history, no full task details."""
    task_id: str
    type: ChallengeType
    points_awarded: int
    completed_at: datetime


class ChallengeHistoryData(BaseModel):
    completed_challenges: List[CompletedChallengeData]
    total_points: int
    total_completed: int


# ── Composed Responses ────────────────────────────────────────────────────────

AllChallengesResponse = ApiResponse[AllChallengesData]
ChallengeTaskResponse = ApiResponse[ChallengeTaskData]
CompleteChallengeResponse = ApiResponse[CompleteChallengeData]
ChallengeHistoryResponse = ApiResponse[ChallengeHistoryData]