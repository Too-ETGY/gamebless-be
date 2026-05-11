from datetime import datetime, timezone
from app.db.repositories.user_repo import UserRepository
from app.schemas.auth import SyncRequest, UserData, ProfileData, AccountStatsData
import logging

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def sync_user(self, uid: str, payload: SyncRequest) -> UserData:
        """
        Called on every login and on profile update.

        First login  → creates the user document with default account_stats
        Return visit → merges only the profile fields sent, leaves stats untouched
        """
        existing = self.repo.get_by_id(uid)
        # now = datetime.now(timezone.utc)

        profile = {
            "username": payload.username,
            "email": payload.email,
            "full_name": payload.full_name,
            "avatar_url": payload.avatar_url,
            "birth_date": payload.birth_date,
            "location": payload.location,
            "gender": payload.gender,
            "occupation": payload.occupation,
        }

        if existing is None:
            # ── First login: create full document ─────────────────────────────
            logger.info(f"New user synced: {uid}")
            data = {
                "profile": profile,
                "account_stats": {
                    "total_points": 0,
                    "current_streak": 0,
                    "highest_streak": 0,
                    "last_access_timestamp": None,
                    "join_date": datetime.now(timezone.utc),  # Set here to ensure it's only set on first sync
                },
            }
        else:
            # ── Return visit: update profile only, preserve stats ─────────────
            logger.info(f"Existing user synced: {uid}")
            data = {"profile": profile}

        updated = self.repo.upsert(uid, data)
        return self._to_user_full_data(uid, updated)

    # def get_me(self, uid: str) -> UserData | None:
    #     """Fetch user profile for /me endpoint."""
    #     doc = self.repo.get_by_id(uid)
    #     if doc is None:
    #         return None
    #     return self._to_user_data(uid, doc)

    def get_me(self, uid: str) -> ProfileData | None:
        doc = self.repo.get_profile_by_id(uid)
        if doc is None:
            return None
        return self._to_profile_data(doc)

    def _to_profile_data(self, doc: dict) -> ProfileData:
        profile = doc
        return ProfileData(**profile)

    def _to_user_full_data(self, uid: str, doc: dict) -> UserData:
        """Map raw Firestore document → UserData schema."""
        profile = doc.get("profile", {})
        stats = doc.get("account_stats", {})

        return UserData(
            uid=uid,
            profile=ProfileData(**profile),
            account_stats=AccountStatsData(**stats),
        )