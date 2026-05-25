from datetime import datetime, timezone, date, timedelta
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.challenge_repo import ChallengeRepository
from app.schemas.progress import AttemptData, ProgressReportData, DailyProgressData
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)

MAX_REPORT_DAYS = 90


class ProgressService:
    def __init__(
        self,
        progress_repo: ProgressRepository,
        user_repo: UserRepository,
        challenge_repo: ChallengeRepository,
    ):
        self.progress_repo = progress_repo
        self.user_repo = user_repo
        self.challenge_repo = challenge_repo

    def record_attempt(self, uid: str) -> AttemptData:
        today = date.today().isoformat()
        updated = self.progress_repo.record_attempt(uid, today)
        return AttemptData(access_attempts_count=updated["attempt_count"])

    def get_progress_report(self, uid: str) -> ProgressReportData:
        user_doc = self.user_repo.get_by_id(uid)
        if user_doc is None:
            raise AppException(status_code=404, message="User not found.")

        profile = user_doc["profile"]
        join_date = profile.get("join_date")
        if isinstance(join_date, str):
            join_date = datetime.fromisoformat(join_date)

        today = date.today()
        join_day = join_date.date()
        days_since_joined = (today - join_day).days

        is_capped = days_since_joined > MAX_REPORT_DAYS
        start_day = today - timedelta(days=MAX_REPORT_DAYS) if is_capped else join_day

        # Fetch attempt docs in range
        attempt_docs = self.progress_repo.get_range(uid, start_day.isoformat(), today.isoformat())
        attempt_map = {doc["date"]: doc for doc in attempt_docs}

        # Fetch completed challenges — group by completed_date
        completed = self.challenge_repo.get_completed(uid)
        completed_by_date: dict[str, int] = {}
        total_challenges_by_type: dict[str, int] = {}

        for c in completed:
            d_obj = c.get("completed_date") or c.get("completed_at")
            if hasattr(d_obj, "isoformat"):
                d = d_obj.isoformat()[:10]
            elif isinstance(d_obj, str):
                d = d_obj[:10]
            else:
                d = str(d_obj)[:10] if d_obj else ""
                
            if d:
                completed_by_date[d] = completed_by_date.get(d, 0) + 1
            ctype = c.get("type", "unknown")
            total_challenges_by_type[ctype] = total_challenges_by_type.get(ctype, 0) + 1

        # Build daily logs + streak scan
        daily_logs = []
        current_run = 0
        highest_streak = 0
        current_day = start_day

        while current_day <= today:
            date_str = current_day.isoformat()
            attempt_doc = attempt_map.get(date_str)
            attempt_count = attempt_doc.get("attempt_count", 0) if attempt_doc else 0
            streak_maintained = attempt_count == 0

            daily_logs.append(DailyProgressData(
                date=date_str,
                streak_maintained=streak_maintained,
                access_attempts_count=attempt_count,
                completed_challenges_count=completed_by_date.get(date_str, 0),
            ))

            if streak_maintained:
                current_run += 1
                highest_streak = max(highest_streak, current_run)
            else:
                current_run = 0

            current_day += timedelta(days=1)

        # current_streak — scan backwards from today
        current_streak = 0
        for log in reversed(daily_logs):
            if log.streak_maintained:
                current_streak += 1
            else:
                break

        return ProgressReportData(
            join_date=join_date,
            days_since_joined=days_since_joined,
            current_streak=current_streak,
            highest_streak=highest_streak,
            total_challenges_by_type=total_challenges_by_type,
            daily_logs=daily_logs,
            is_capped=is_capped,
            cap_days=MAX_REPORT_DAYS,
        )


def get_progress_service(progress_repo, user_repo, challenge_repo) -> ProgressService:
    return ProgressService(progress_repo, user_repo, challenge_repo)