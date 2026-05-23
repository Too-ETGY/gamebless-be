from google.cloud.firestore_v1 import Client
from google.cloud.firestore import Increment
from app.models.progress import UserProgress
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
        docs = self._subcollection(uid).stream()
        return [
            {"date": doc.id, **doc.to_dict()}
            for doc in docs
            if from_date <= doc.id <= to_date
        ]

    def record_attempt(self, uid: str, date_str: str) -> dict:
        """
        Creates or increments today's attempt document.
        Uses UserProgress model for first-time creation shape.
        """
        ref = self._ref(uid, date_str)
        existing = ref.get()

        if not existing.exists:
            progress = UserProgress(
                attempt_count=1,
                last_attempt_at=datetime.now(timezone.utc),
            )
            ref.set(progress.model_dump())
        else:
            ref.update({
                "attempt_count": Increment(1),
                "last_attempt_at": datetime.now(timezone.utc),
            })

        updated = ref.get()
        return {"date": updated.id, **updated.to_dict()}


def get_progress_repository(db: Client) -> ProgressRepository:
    return ProgressRepository(db)