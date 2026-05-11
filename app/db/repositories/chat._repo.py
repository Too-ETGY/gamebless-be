from google.cloud.firestore_v1 import Client
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"
CHATS_SUBCOLLECTION = "chats"


class ChatRepository:
    def __init__(self, db: Client):
        self.db = db

    def _collection_ref(self, uid: str):
        return (
            self.db
            .collection(USERS_COLLECTION)
            .document(uid)
            .collection(CHATS_SUBCOLLECTION)
        )

    def save_message(self, uid: str, data: dict) -> dict:
        """Save a single message. Returns saved doc with auto-generated ID."""
        ref = self._collection_ref(uid).document()   # auto-generated ID
        data["timestamp"] = datetime.now(timezone.utc)
        ref.set(data)
        return {"id": ref.id, **data}

    def get_session_history(self, uid: str, session_id: str, limit: int = 20) -> list[dict]:
        """
        Fetch recent messages for a session.
        Used by AI service to build conversation context.
        """
        docs = (
            self._collection_ref(uid)
            .where("session_id", "==", session_id)
            .order_by("timestamp")
            .limit_to_last(limit)
            .stream()
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def get_chat_repository(db: Client) -> ChatRepository:
    return ChatRepository(db)