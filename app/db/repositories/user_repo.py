from google.cloud.firestore_v1 import Client
from google.cloud.firestore import Increment
from datetime import datetime
from app.models.user import UserProfile, AccountStats
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
        Uses UserProfile and AccountStats models to construct the document.
        Defaults are guaranteed by the models — no manual field listing needed.
        """
        profile = UserProfile(email=email, avatar_url=avatar_url)
        stats = AccountStats(join_date=join_date)

        data = {
            "profile": profile.model_dump(),
            "account_stats": stats.model_dump(),
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
        return ref.get().to_dict()["account_stats"]["total_points"]

    def reset_streak(self, uid: str) -> None:
        self.collection.document(uid).update({"account_stats.current_streak": 0})

    def increment_streak(self, uid: str) -> None:
        self.collection.document(uid).update(
            {"account_stats.current_streak": Increment(1)}
        )

    def exists(self, uid: str) -> bool:
        return self.collection.document(uid).get().exists


def get_user_repository(db: Client) -> UserRepository:
    return UserRepository(db)