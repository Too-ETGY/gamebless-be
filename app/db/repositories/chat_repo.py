from google.cloud.firestore_v1 import Client
from google.cloud.firestore import Increment
from app.models.chat import ChatSession, ChatMessage, SenderType
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"
SESSIONS_SUBCOLLECTION = "chat_sessions"
MESSAGES_SUBCOLLECTION = "messages"

# When message_count hits this, summarization should be triggered
SUMMARY_THRESHOLD = 10


class ChatRepository:
    def __init__(self, db: Client):
        self.db = db

    def _sessions_ref(self, uid: str):
        return (
            self.db
            .collection(USERS_COLLECTION)
            .document(uid)
            .collection(SESSIONS_SUBCOLLECTION)
        )

    def _messages_ref(self, uid: str, session_id: str):
        return (
            self._sessions_ref(uid)
            .document(session_id)
            .collection(MESSAGES_SUBCOLLECTION)
        )

    # ── Sessions ──────────────────────────────────────────────────────────────

    def create_session(self, uid: str, title: str | None) -> dict:
        """Create a new chat session. Uses ChatSession model for construction."""
        session = ChatSession(title=title)
        ref = self._sessions_ref(uid).document()    # auto-generated ID
        ref.set(session.model_dump())
        return {"session_id": ref.id, **session.model_dump()}

    def get_session(self, uid: str, session_id: str) -> dict | None:
        """Fetch session — also validates ownership since it's under users/{uid}."""
        doc = self._sessions_ref(uid).document(session_id).get()
        if not doc.exists:
            return None
        return {"session_id": doc.id, **doc.to_dict()}

    def get_all_sessions(self, uid: str) -> list[dict]:
        """List all sessions for a user, ordered by most recent."""
        docs = (
            self._sessions_ref(uid)
            .order_by("updated_at", direction="DESCENDING")
            .stream()
        )
        return [{"session_id": doc.id, **doc.to_dict()} for doc in docs]

    def increment_message_count(self, uid: str, session_id: str) -> int:
        """Atomically increment message_count and update updated_at. Returns new count."""
        ref = self._sessions_ref(uid).document(session_id)
        ref.update({
            "message_count": Increment(1),
            "updated_at": datetime.now(timezone.utc),
        })
        return ref.get().to_dict()["message_count"]

    def save_summary(self, uid: str, session_id: str, summary: str) -> None:
        """Save AI-generated summary and reset message_count for next threshold cycle."""
        self._sessions_ref(uid).document(session_id).update({
            "summary": summary,
            "message_count": 0,         # reset so threshold triggers again after 10 more
            "updated_at": datetime.now(timezone.utc),
        })

    # ── Messages ──────────────────────────────────────────────────────────────

    def save_message(self, uid: str, session_id: str, sender: SenderType, content: str) -> dict:
        """Save a single message. Uses ChatMessage model for construction."""
        message = ChatMessage(session_id=session_id, sender=sender, content=content)
        ref = self._messages_ref(uid, session_id).document()    # auto-generated ID
        ref.set(message.model_dump())
        return {"message_id": ref.id, **message.model_dump()}

    def get_recent_messages(self, uid: str, session_id: str, limit: int = 10) -> list[dict]:
        """
        Fetch the most recent N messages for RAG context building.
        Ordered ascending so they read chronologically in the prompt.
        """
        docs = (
            self._messages_ref(uid, session_id)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        messages = [{"message_id": doc.id, **doc.to_dict()} for doc in docs]
        return list(reversed(messages))     # flip back to chronological

    def get_all_messages(self, uid: str, session_id: str) -> list[dict]:
        """Fetch all messages in a session chronologically."""
        docs = (
            self._messages_ref(uid, session_id)
            .order_by("timestamp")
            .stream()
        )
        return [{"message_id": doc.id, **doc.to_dict()} for doc in docs]

    def needs_summarization(self, uid: str, session_id: str) -> bool:
        """Check if session has hit the message threshold."""
        session = self.get_session(uid, session_id)
        if session is None:
            return False
        return session.get("message_count", 0) >= SUMMARY_THRESHOLD


def get_chat_repository(db: Client) -> ChatRepository:
    return ChatRepository(db)