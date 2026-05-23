from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas.common import ApiResponse


# ── Response Data ─────────────────────────────────────────────────────────────

class DailyProgressData(BaseModel):
    date: str                           # "YYYY-MM-DD"
    streak_maintained: bool
    access_attempts_count: int
    completed_challenges_count: int

class ProgressReportData(BaseModel):
    # Account level
    join_date: datetime
    days_since_joined: int
    current_streak: int
    highest_streak: int                 # computed by scanning progress history

    # Aggregated totals from join_date
    total_challenges_by_type: dict      # {"video": 12, "article": 4, "funfact": 1}

    # Daily calendar from join_date (capped at MAX_REPORT_DAYS)
    daily_logs: List[DailyProgressData]
    is_capped: bool                     # True if join_date exceeds the cap
    cap_days: int                       # so frontend knows the cap value


class AttemptData(BaseModel):
    access_attempts_count: int          # updated count for today


# ── Composed Responses ────────────────────────────────────────────────────────

AttemptResponse = ApiResponse[AttemptData]
ProgressReportResponse = ApiResponse[ProgressReportData]