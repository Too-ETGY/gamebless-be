from google.cloud.firestore_v1 import Client
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
        """Fetch a single day's progress. date_str: 'YYYY-MM-DD'"""
        doc = self._ref(uid, date_str).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict()}

    def upsert(self, uid: str, date_str: str, data: dict) -> dict:
        """Create or update a progress document."""
        ref = self._ref(uid, date_str)
        ref.set(data, merge=True)
        updated = ref.get()
        return {"id": updated.id, **updated.to_dict()}

    def increment_access_try(self, uid: str, date_str: str) -> None:
        """Atomically increment today_access_try by 1."""
        from google.cloud.firestore_v1 import Increment
        ref = self._ref(uid, date_str)
        ref.set({"today_access_try": Increment(1)}, merge=True)


def get_progress_repository(db: Client) -> ProgressRepository:
    return ProgressRepository(db)