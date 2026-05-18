from datetime import datetime, timezone, date, timedelta
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.user_repo import UserRepository
from app.schemas.progress import AttemptData, ProgressReportData, DailyProgressData
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)

MAX_REPORT_DAYS = 90  # increase this as needed


class ProgressService:
    def __init__(self, progress_repo: ProgressRepository, user_repo: UserRepository):
        self.progress_repo = progress_repo
        self.user_repo = user_repo

    def record_attempt(self, uid: str) -> AttemptData:
        today = date.today().isoformat()
        existing = self.progress_repo.get_by_date(uid, today)
        first_attempt_today = existing is None or existing.get("access_attempts_count", 0) == 0
        updated = self.progress_repo.record_attempt(uid, today)
        if first_attempt_today:
            self.user_repo.reset_streak(uid)
            logger.info(f"Streak reset for user {uid}")
        user_doc = self.user_repo.get_by_id(uid)
        return AttemptData(
            access_attempts_count=updated["access_attempts_count"],
            current_streak=user_doc["account_stats"]["current_streak"],
        )

    def get_progress_report(self, uid: str) -> ProgressReportData:
        user_doc = self.user_repo.get_by_id(uid)
        if user_doc is None:
            raise AppException(status_code=404, message="User not found.")

        stats = user_doc["account_stats"]
        join_date = stats["join_date"]
        if isinstance(join_date, str):
            join_date = datetime.fromisoformat(join_date)

        today = date.today()
        join_day = join_date.date()
        days_since_joined = (today - join_day).days

        is_capped = days_since_joined > MAX_REPORT_DAYS
        start_day = today - timedelta(days=MAX_REPORT_DAYS) if is_capped else join_day

        real_docs = self.progress_repo.get_range(uid, start_day.isoformat(), today.isoformat())
        real_docs_map = {doc["date"]: doc for doc in real_docs}

        daily_logs = []
        total_challenges_by_type = {}
        current_run = 0
        highest_streak = 0
        current_day = start_day

        while current_day <= today:
            date_str = current_day.isoformat()
            doc = real_docs_map.get(date_str)

            if doc:
                attempts = doc.get("access_attempts_count", 0)
                streak_maintained = attempts == 0
                challenges_by_type = doc.get("challenges_by_type", {})
                for ctype, count in challenges_by_type.items():
                    total_challenges_by_type[ctype] = total_challenges_by_type.get(ctype, 0) + count
            else:
                attempts = 0
                streak_maintained = True
                challenges_by_type = {}

            daily_logs.append(DailyProgressData(
                date=date_str,
                streak_maintained=streak_maintained,
                access_attempts_count=attempts,
                challenges_by_type=challenges_by_type,
            ))

            if streak_maintained:
                current_run += 1
                highest_streak = max(highest_streak, current_run)
            else:
                current_run = 0

            current_day += timedelta(days=1)

        return ProgressReportData(
            join_date=join_date,
            days_since_joined=days_since_joined,
            current_streak=stats["current_streak"],
            highest_streak=highest_streak,
            total_challenges_by_type=total_challenges_by_type,
            daily_logs=daily_logs,
            is_capped=is_capped,
            cap_days=MAX_REPORT_DAYS,
        )