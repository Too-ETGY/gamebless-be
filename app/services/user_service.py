from datetime import datetime, timezone, date
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.challenge_repo import ChallengeRepository
from app.schemas.user import ProfileData, AccountStatsData, MeData
from app.schemas.auth import SyncData
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        progress_repo: ProgressRepository,
        challenge_repo: ChallengeRepository,
    ):
        self.user_repo = user_repo
        self.progress_repo = progress_repo
        self.challenge_repo = challenge_repo

    def sync(self, uid: str, email: str) -> SyncData:
        existing = self.user_repo.get_by_id(uid)
        if existing:
            return SyncData(
                is_new_user=False,
                profile=self._to_profile(uid, existing["profile"]),
            )
        now = datetime.now(timezone.utc)
        doc = self.user_repo.create(uid, email)
        logger.info(f"New user created: {uid}")
        full_doc = self.user_repo.get_by_id(uid)
        return SyncData(
            is_new_user=True,
            profile=self._to_profile(uid, full_doc["profile"]),
            account_stats=self._compute_stats(uid, full_doc["profile"]),
        )

    def get_me(self, uid: str) -> MeData:
        doc = self.user_repo.get_by_id(uid)
        if doc is None:
            raise AppException(status_code=404, message="User not found. Please sync first.")

        profile = self._to_profile(uid, doc["profile"])
        stats = self._compute_stats(uid, doc["profile"])
        return MeData(profile=profile, account_stats=stats)

    def update_profile(self, uid: str, fields: dict) -> ProfileData:
        if not self.user_repo.exists(uid):
            raise AppException(status_code=404, message="User not found.")
        updated = self.user_repo.update_profile(uid, fields)
        return self._to_profile(uid, updated["profile"])

    def _compute_stats(self, uid: str, profile: dict) -> AccountStatsData:
        # total_points — sum from completed_challenges
        completed = self.challenge_repo.get_completed(uid)
        total_points = sum(c.get("points", 0) for c in completed)

        # days_since_joined
        join_date = profile.get("join_date")
        if isinstance(join_date, str):
            join_date = datetime.fromisoformat(join_date)
        days_since_joined = (datetime.now(timezone.utc) - join_date).days if join_date else 0

        # current_streak — scan backwards from today
        # a day with a progress doc = streak broken, no doc = streak maintained
        current_streak = 0
        today = date.today()
        check_day = today

        while True:
            date_str = check_day.isoformat()
            # stop scanning before join_date
            if join_date and check_day < join_date.date():
                break
            progress = self.progress_repo.get_by_date(uid, date_str)
            if progress and progress.get("attempt_count", 0) > 0:
                break
            current_streak += 1
            from datetime import timedelta
            check_day -= timedelta(days=1)

            # safety cap — don't scan more than 365 days
            if (today - check_day).days > 365:
                break

        return AccountStatsData(
            total_points=total_points,
            current_streak=current_streak,
            days_since_joined=days_since_joined,
        )

    def _to_profile(self, uid: str, profile: dict) -> ProfileData:
        return ProfileData(uid=uid, **profile)


def get_user_service(user_repo, progress_repo, challenge_repo) -> UserService:
    return UserService(user_repo, progress_repo, challenge_repo)