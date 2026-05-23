from pydantic import BaseModel
from typing import List, Optional
from app.models.challenge import ChallengeType
from app.schemas.common import ApiResponse


# ── Response Data ─────────────────────────────────────────────────────────────

class ChallengeTaskData(BaseModel):
    task_id: str
    type: ChallengeType
    content_url: Optional[str] = None
    point_value: int
    question: Optional[str] = None
    is_completed: bool = False          # marked per user at query time


class AllChallengesData(BaseModel):
    challenges: List[ChallengeTaskData]
    total: int


class CompleteChallengeData(BaseModel):
    task_id: str
    points_awarded: int
    total_points: int                   # updated account_stats.total_points


class ChallengeHistoryData(BaseModel):
    completed_challenges: List[ChallengeTaskData]
    total_points: int                   # from account_stats directly


# ── Composed Responses ────────────────────────────────────────────────────────
ChallengeResponse = ApiResponse[ChallengeTaskData]
AllChallengesResponse = ApiResponse[AllChallengesData]
CompleteChallengeResponse = ApiResponse[CompleteChallengeData]
ChallengeHistoryResponse = ApiResponse[ChallengeHistoryData]