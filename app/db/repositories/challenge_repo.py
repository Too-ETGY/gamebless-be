from google.cloud.firestore_v1 import Client
import logging

logger = logging.getLogger(__name__)

CHALLENGES_COLLECTION = "challenges"


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


def get_challenge_repository(db: Client) -> ChallengeRepository:
    return ChallengeRepository(db)