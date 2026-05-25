from google.cloud.firestore_v1 import Client
from google.cloud.firestore import Increment
from app.models.chat import ChatSession, ChatMessage, SenderType
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"
SESSIONS_SUBCOLLECTION = "chat_sessions"
MESSAGES_SUBCOLLECTION = "messages"

SUMMARY_THRESHOLD = 20      # messages before summarization
SESSION_MAX_DAYS = 7        # days before session is archived + messages deleted


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

    def create_session(self, uid: str, title: str | None = None, summary: str | None = None) -> dict:
        session = ChatSession(title=title, summary=summary)
        ref = self._sessions_ref(uid).document()
        ref.set(session.model_dump())
        return {"session_id": ref.id, **session.model_dump()}

    def get_session(self, uid: str, session_id: str) -> dict | None:
        doc = self._sessions_ref(uid).document(session_id).get()
        if not doc.exists:
            return None
        return {"session_id": doc.id, **doc.to_dict()}

    def get_active_session(self, uid: str) -> dict | None:
        """Returns most recent active session."""
        docs = (
            self._sessions_ref(uid)
            .where("is_active", "==", True)
            .order_by("updated_at", direction="DESCENDING")
            .limit(1)
            .stream()
        )
        for doc in docs:
            return {"session_id": doc.id, **doc.to_dict()}
        return None

    def archive_session(self, uid: str, session_id: str, summary: str) -> None:
        """Mark session as inactive and save summary."""
        self._sessions_ref(uid).document(session_id).update({
            "is_active": False,
            "summary": summary,
            "updated_at": datetime.now(timezone.utc),
        })

    def delete_messages(self, uid: str, session_id: str) -> None:
        """Delete all messages in a session. Called only for sessions older than SESSION_MAX_DAYS."""
        docs = self._messages_ref(uid, session_id).stream()
        for doc in docs:
            doc.reference.delete()
        logger.info(f"Deleted messages for session {session_id}")

    def increment_message_count(self, uid: str, session_id: str) -> int:
        ref = self._sessions_ref(uid).document(session_id)
        ref.update({
            "message_count": Increment(1),
            "updated_at": datetime.now(timezone.utc),
        })
        return ref.get().to_dict()["message_count"]

    def get_session_age_days(self, uid: str, session_id: str) -> int:
        session = self.get_session(uid, session_id)
        if not session:
            return 0
        created_at = session.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return (datetime.now(timezone.utc) - created_at).days

    def needs_rotation_by_count(self, uid: str, session_id: str) -> bool:
        session = self.get_session(uid, session_id)
        return session.get("message_count", 0) >= SUMMARY_THRESHOLD if session else False

    def needs_rotation_by_age(self, uid: str, session_id: str) -> bool:
        return self.get_session_age_days(uid, session_id) >= SESSION_MAX_DAYS

    # ── Messages ──────────────────────────────────────────────────────────────

    def save_message(
        self,
        uid: str,
        session_id: str,
        sender: SenderType,
        content: str,
        reply_to: str | None = None,
    ) -> dict:
        message = ChatMessage(
            session_id=session_id,
            sender=sender,
            content=content,
            reply_to=reply_to,
        )
        ref = self._messages_ref(uid, session_id).document()
        ref.set(message.model_dump())
        return {"message_id": ref.id, **message.model_dump()}

    def get_recent_messages(self, uid: str, session_id: str, limit: int = 10) -> list[dict]:
        docs = (
            self._messages_ref(uid, session_id)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        messages = [{"message_id": doc.id, **doc.to_dict()} for doc in docs]
        return list(reversed(messages))

    def get_all_messages(self, uid: str, session_id: str) -> list[dict]:
        docs = (
            self._messages_ref(uid, session_id)
            .order_by("timestamp")
            .stream()
        )
        return [{"message_id": doc.id, **doc.to_dict()} for doc in docs]


def get_chat_repository(db: Client) -> ChatRepository:
    return ChatRepository(db)