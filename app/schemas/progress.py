from pydantic import BaseModel
from typing import Optional, List
from app.schemas.common import ApiResponse
from app.schemas.auth import AccountStatsData


# ── Response Data ─────────────────────────────────────────────────────────────

class DailyProgressData(BaseModel):
    date: str                               # "YYYY-MM-DD"
    completed_challenges: List[str]         # array of task_ids
    today_points_earned: int
    streak_maintained: Optional[bool] = None
    ai_summary: Optional[str] = None       # psychologist note, null until triggered
    today_access_try: int                  # how many times user tried to access judol


class ProgressData(BaseModel):
    account_stats: AccountStatsData
    today: Optional[DailyProgressData] = None   # today's progress document


class TriggerAnalysisData(BaseModel):
    ai_summary: str
    date: str


# ── Points ────────────────────────────────────────────────────────────────────

class PointsBalanceData(BaseModel):
    total_points: int
    current_streak: int


# ── Composed Responses ────────────────────────────────────────────────────────

ProgressResponse = ApiResponse[ProgressData]
TriggerAnalysisResponse = ApiResponse[TriggerAnalysisData]
PointsBalanceResponse = ApiResponse[PointsBalanceData]