from datetime import datetime, timezone
from app.db.repositories.user_repo import UserRepository
from app.schemas.auth import SyncData
from app.schemas.user import ProfileData, AccountStatsData, MeData
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def sync(self, uid: str, email: str) -> SyncData:
        existing = self.repo.get_by_id(uid)
        if existing:
            logger.info(f"Sync called for existing user: {uid}")
            return SyncData(
                is_new_user=False,
                profile=self._to_profile(uid, existing["profile"]),
                account_stats=AccountStatsData(**existing["account_stats"]),
            )
        now = datetime.now(timezone.utc)
        doc = self.repo.create(uid, email, now)
        logger.info(f"New user created: {uid}")
        return SyncData(
            is_new_user=True,
            profile=self._to_profile(uid, existing["profile"]),
            account_stats=AccountStatsData(**doc['account_stats']),
        )

    def get_me(self, uid: str) -> MeData:
        doc = self.repo.get_by_id(uid)
        if doc is None:
            raise AppException(status_code=404, message="User not found. Please sync first.")
        return MeData(
            profile=self._to_profile(uid, doc["profile"]),
            account_stats=AccountStatsData(**doc["account_stats"]),
        )

    def update_profile(self, uid: str, fields: dict) -> ProfileData:
        if not self.repo.exists(uid):
            raise AppException(status_code=404, message="User not found.")
        updated = self.repo.update_profile(uid, fields)
        return self._to_profile(uid, updated["profile"])

    def _to_profile(self, uid: str, profile: dict) -> ProfileData:
        return ProfileData(uid=uid, **profile)


def get_user_service(repo: UserRepository) -> UserService:
    return UserService(repo)