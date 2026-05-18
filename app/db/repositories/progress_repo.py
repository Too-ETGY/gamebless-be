from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1 import Increment, ArrayUnion
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"
PROGRESS_SUBCOLLECTION = "progress"


class ProgressRepository:
    def __init__(self, db: Client):
        self.db = db

    def _ref(self, uid: str, date_str: str):
        return (
            self.db
            .collection(USERS_COLLECTION)
            .document(uid)
            .collection(PROGRESS_SUBCOLLECTION)
            .document(date_str)
        )

    def get_by_date(self, uid: str, date_str: str) -> dict | None:
        doc = self._ref(uid, date_str).get()
        if not doc.exists:
            return None
        return {"date": doc.id, **doc.to_dict()}

    def get_range(self, uid: str, from_date: str, to_date: str) -> list[dict]:
        """
        Fetch all progress documents between two dates (inclusive).
        Returns only documents that exist — caller handles missing days.
        """
        docs = (
            self.db
            .collection(USERS_COLLECTION)
            .document(uid)
            .collection(PROGRESS_SUBCOLLECTION)
            .where("__name__", ">=", from_date)
            .where("__name__", "<=", to_date)
            .stream()
        )
        return [{"date": doc.id, **doc.to_dict()} for doc in docs]

    def record_attempt(self, uid: str, date_str: str) -> dict:
        """
        Atomically increment access_attempts_count.
        Creates the document if it doesn't exist yet (merge=True).
        Also sets streak_maintained = False.
        """
        ref = self._ref(uid, date_str)
        ref.set({
            "access_attempts_count": Increment(1),
            "streak_maintained": False,
            "updated_at": datetime.now(timezone.utc),
            # defaults for new doc
            "completed_challenges": [],
            "challenges_by_type": {},
        }, merge=True)
        updated = ref.get()
        return {"date": updated.id, **updated.to_dict()}

    def complete_challenge(
        self,
        uid: str,
        date_str: str,
        task_id: str,
        challenge_type: str,
    ) -> dict:
        """
        Append task_id to completed_challenges and increment challenges_by_type.
        Creates document if it doesn't exist yet.
        """
        ref = self._ref(uid, date_str)
        ref.set({
            "completed_challenges": ArrayUnion([task_id]),
            f"challenges_by_type.{challenge_type}": Increment(1),
            "streak_maintained": True,
            "updated_at": datetime.now(timezone.utc),
            # defaults for new doc
            "access_attempts_count": 0,
        }, merge=True)
        updated = ref.get()
        return {"date": updated.id, **updated.to_dict()}

    def is_challenge_completed(self, uid: str, date_str: str, task_id: str) -> bool:
        """Deduplication check before awarding points."""
        doc = self.get_by_date(uid, date_str)
        if doc is None:
            return False
        return task_id in doc.get("completed_challenges", [])


def get_progress_repository(db: Client) -> ProgressRepository:
    return ProgressRepository(db)