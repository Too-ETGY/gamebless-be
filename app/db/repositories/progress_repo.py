from google.cloud.firestore_v1 import Client
from google.cloud.firestore import Increment, ArrayUnion
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

    def _subcollection(self, uid: str):
        return (
            self.db
            .collection(USERS_COLLECTION)
            .document(uid)
            .collection(PROGRESS_SUBCOLLECTION)
        )

    def get_by_date(self, uid: str, date_str: str) -> dict | None:
        doc = self._ref(uid, date_str).get()
        if not doc.exists:
            return None
        return {"date": doc.id, **doc.to_dict()}

    def get_range(self, uid: str, from_date: str, to_date: str) -> list[dict]:
        """
        Fetch all progress documents between two dates (inclusive).
        Uses start_at/end_at on document references — correct way to
        filter subcollection documents by ID range in Firestore.
        """
        subcol = self._subcollection(uid)

        from_ref = self._ref(uid, from_date)
        to_ref = self._ref(uid, to_date)

        docs = (
            subcol
            .order_by("__name__")
            .start_at(from_ref)
            .end_at(to_ref)
            .stream()
        )
        return [{"date": doc.id, **doc.to_dict()} for doc in docs]

    def record_attempt(self, uid: str, date_str: str) -> dict:
        ref = self._ref(uid, date_str)
        ref.set({
            "access_attempts_count": Increment(1),
            "streak_maintained": False,
            "updated_at": datetime.now(timezone.utc),
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
        ref = self._ref(uid, date_str)
        ref.set({
            "completed_challenges": ArrayUnion([task_id]),
            f"challenges_by_type.{challenge_type}": Increment(1),
            "updated_at": datetime.now(timezone.utc),
            "access_attempts_count": 0,
        }, merge=True)
        updated = ref.get()
        return {"date": updated.id, **updated.to_dict()}

    def is_challenge_completed(self, uid: str, date_str: str, task_id: str) -> bool:
        doc = self.get_by_date(uid, date_str)
        if doc is None:
            return False
        return task_id in doc.get("completed_challenges", [])


def get_progress_repository(db: Client) -> ProgressRepository:
    return ProgressRepository(db)