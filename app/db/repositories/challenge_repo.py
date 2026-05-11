from google.cloud.firestore_v1 import Client
import logging

logger = logging.getLogger(__name__)

DAILY_CHALLENGES_COLLECTION = "daily_challenges"


class ChallengeRepository:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection(DAILY_CHALLENGES_COLLECTION)

    def get_by_date(self, date_str: str) -> dict | None:
        """Fetch challenge document for a specific date. date_str: 'YYYY-MM-DD'"""
        doc = self.collection.document(date_str).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict()}

    def get_all(self) -> list[dict]:
        """Fetch all challenge documents."""
        docs = self.collection.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def get_challenge_repository(db: Client) -> ChallengeRepository:
    return ChallengeRepository(db)