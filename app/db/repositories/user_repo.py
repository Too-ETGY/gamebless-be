from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1 import Increment
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"


class UserRepository:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection(USERS_COLLECTION)

    def get_by_id(self, uid: str) -> dict | None:
        doc = self.collection.document(uid).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict()}

    def create(self, uid: str, email: str, avatar_url: str | None, join_date: datetime) -> dict:
        """
        First-time sync. Creates minimal user document.
        Everything except email, avatar_url, and join_date is null/0.
        """
        data = {
            "profile": {
                "email": email,
                "avatar_url": avatar_url,
                "username": None,
                "full_name": None,
                "birth_date": None,
                "gender": None,
                "occupation": None,
            },
            "account_stats": {
                "total_points": 0,
                "current_streak": 0,
                "join_date": join_date,
            }
        }
        self.collection.document(uid).set(data)
        logger.info(f"Created user document: {uid}")
        return {"id": uid, **data}

    def update_profile(self, uid: str, fields: dict) -> dict:
        """Partial update — only touches profile sub-fields provided."""
        update_data = {f"profile.{k}": v for k, v in fields.items() if v is not None}
        self.collection.document(uid).update(update_data)
        return self.get_by_id(uid)

    def increment_points(self, uid: str, points: int) -> int:
        """Atomically add points. Returns updated total."""
        ref = self.collection.document(uid)
        ref.update({"account_stats.total_points": Increment(points)})
        updated = ref.get().to_dict()
        return updated["account_stats"]["total_points"]

    def reset_streak(self, uid: str) -> None:
        """Called when user attempts to access a gambling site."""
        self.collection.document(uid).update({"account_stats.current_streak": 0})

    def increment_streak(self, uid: str) -> None:
        """Called by a scheduled job (future) or manually."""
        self.collection.document(uid).update(
            {"account_stats.current_streak": Increment(1)}
        )

    def exists(self, uid: str) -> bool:
        return self.collection.document(uid).get().exists


def get_user_repository(db: Client) -> UserRepository:
    return UserRepository(db)