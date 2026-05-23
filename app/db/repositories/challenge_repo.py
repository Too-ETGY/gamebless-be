from google.cloud.firestore_v1 import Client
from app.models.user import CompletedChallenges
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

CHALLENGES_COLLECTION = "challenges"
USERS_COLLECTION = "users"
COMPLETED_SUBCOLLECTION = "completed_challenges"


class ChallengeRepository:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection(CHALLENGES_COLLECTION)

    def get_all(self) -> list[dict]:
        docs = self.collection.stream()
        return [{"task_id": doc.id, **doc.to_dict()} for doc in docs]

    def get_by_id(self, task_id: str) -> dict | None:
        doc = self.collection.document(task_id).get()
        if not doc.exists:
            return None
        return {"task_id": doc.id, **doc.to_dict()}

    def get_by_type(self, challenge_type: str) -> list[dict]:
        docs = self.collection.where("type", "==", challenge_type).stream()
        return [{"task_id": doc.id, **doc.to_dict()} for doc in docs]

    # ── Completed Subcollection ───────────────────────────────────────────────

    def _completed_ref(self, uid: str):
        return (
            self.db
            .collection(USERS_COLLECTION)
            .document(uid)
            .collection(COMPLETED_SUBCOLLECTION)
        )

    def get_completed(self, uid: str) -> list[dict]:
        docs = self._completed_ref(uid).stream()
        return [{"task_id": doc.id, **doc.to_dict()} for doc in docs]

    def get_completed_ids(self, uid: str) -> set[str]:
        """Lightweight fetch — only document IDs, no field data."""
        return {doc.id for doc in self._completed_ref(uid).stream()}

    def is_completed(self, uid: str, task_id: str) -> bool:
        return self._completed_ref(uid).document(task_id).get().exists

    def save_completed(self, uid: str, task_id: str, challenge_type: str, points: int) -> dict:
        completed = CompletedChallenges(type=challenge_type, points=points)
        data = completed.model_dump()
        self._completed_ref(uid).document(task_id).set(data)
        return {"task_id": task_id, **data}


def get_challenge_repository(db: Client) -> ChallengeRepository:
    return ChallengeRepository(db)