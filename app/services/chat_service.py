from google.genai import types
from app.db.repositories.chat_repo import ChatRepository
from app.db.gemini_client import get_genai_client
from app.models.chat import SenderType
from app.schemas.chat import SessionData, MessageData, SendMessageData, MessageListData
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"

PSYCHOLOGIST_SYSTEM_PROMPT = """
You are Bless, a warm and empathetic AI companion integrated into an anti-online-gambling app.
Your role is to act as a supportive psychological companion — not a licensed therapist, but a
caring, non-judgmental presence that helps users reflect on their habits, stay motivated, and
build healthier digital behaviors.

Your responsibilities:
- Provide emotional support and encouragement to users trying to reduce gambling behavior
- Celebrate their progress (streaks, completed challenges, clean days)
- Help them identify triggers and suggest healthy coping strategies
- Guide them toward the app's daily challenges when relevant
- Keep conversations warm, conversational, and human — avoid clinical language

Boundaries you must strictly follow:
- Never encourage, glorify, or discuss gambling strategies or sites
- Never provide medical or psychiatric diagnoses
- If a user expresses thoughts of self-harm, gently refer them to professional help
- Keep responses concise — 2 to 4 sentences unless the user needs more
- Always respond in the same language the user uses (Bahasa Indonesia or English)
"""


class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    # ── Active Session ────────────────────────────────────────────────────────

    def get_or_create_active_session(self, uid: str) -> SessionData:
        """
        Returns the user's current active session.
        Creates one automatically if none exists.

        Frontend calls this on app open — stores the session_id locally
        and uses it for all subsequent message calls. User never sees
        or manages sessions manually.
        """
        sessions = self.repo.get_all_sessions(uid)

        if sessions:
            # Most recent session is always first (ordered by updated_at DESC)
            return self._to_session_data(sessions[0])

        # First time — create session silently
        doc = self.repo.create_session(uid, title=None)
        logger.info(f"Auto-created first session for user {uid}")
        return self._to_session_data(doc)

    # ── Messages ──────────────────────────────────────────────────────────────

    def get_messages(self, uid: str, session_id: str) -> MessageListData:
        self._assert_session_owned(uid, session_id)
        docs = self.repo.get_all_messages(uid, session_id)
        messages = [self._to_message_data(d) for d in docs]
        session = self.repo.get_session(uid, session_id)
        return MessageListData(
            messages=messages,
            total=len(messages),
            has_summary=session.get("summary") is not None,
        )

    # ── Core: Send Message ────────────────────────────────────────────────────

    def send_message(self, uid: str, session_id: str, content: str) -> SendMessageData:
        """
        Main flow:
        1. Validate session ownership
        2. Save user message
        3. Build context (history + optional summary)
        4. Call Gemini
        5. Save AI response
        6. Increment message count — archive session and start fresh if threshold hit
        """
        self._assert_session_owned(uid, session_id)

        # 1. Save user message
        user_msg = self.repo.save_message(uid, session_id, SenderType.USER, content)

        # 2. Build context
        history = self.repo.get_recent_messages(uid, session_id, limit=10)
        session = self.repo.get_session(uid, session_id)
        context = self._build_context(history, session.get("summary"))

        # 3. Call Gemini
        ai_content = self._call_llm(context, content)

        # 4. Save AI response
        ai_msg = self.repo.save_message(uid, session_id, SenderType.AI, ai_content)

        # 5. Increment count per message pair (user + ai = 2)
        self.repo.increment_message_count(uid, session_id)
        self.repo.increment_message_count(uid, session_id)

        # 6. Check threshold — summarize and silently rotate to a new session
        if self.repo.needs_summarization(uid, session_id):
            self._summarize_and_rotate(uid, session_id)

        return SendMessageData(
            user_message=self._to_message_data(user_msg),
            ai_message=self._to_message_data(ai_msg),
        )

    # ── LLM ───────────────────────────────────────────────────────────────────

    def _call_llm(self, context: list, user_content: str) -> str:
        client = get_genai_client()

        contents = context + [
            types.Content(
                role="user",
                parts=[types.Part(text=user_content)],
            )
        ]

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=PSYCHOLOGIST_SYSTEM_PROMPT,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=512,
            ),
        )

        return response.text

    def _build_context(self, history: list[dict], summary: str | None) -> list:
        """
        Converts stored messages into Gemini content format.
        Injects summary as prior context if session was previously summarized.
        """
        contents = []

        if summary:
            contents.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text=f"[Previous conversation summary: {summary}]")],
                )
            )

        role_map = {SenderType.USER: "user", SenderType.AI: "model"}
        for msg in history:
            role = role_map.get(msg["sender"], "user")
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])],
                )
            )

        return contents

    # ── Session Rotation (scaffolded) ─────────────────────────────────────────

    def _summarize_and_rotate(self, uid: str, session_id: str) -> None:
        """
        TODO: next session
        Called when message_count hits SUMMARY_THRESHOLD.

        Plan:
        1. Fetch all messages from current session
        2. Ask Gemini to summarize the conversation
        3. Create a new session, carrying the summary forward as context
        4. Frontend gets new session_id on next get_or_create_active_session() call

        User never notices — conversation just continues seamlessly.
        """
        pass

    # ── RAG (scaffolded) ──────────────────────────────────────────────────────

    def _fetch_rag_context(self, uid: str, user_message: str) -> str:
        """
        TODO: next session
        Retrieves relevant context from vector DB.
        Sources: user profile, progress history, challenge history, past chats.
        Returns formatted string injected into system prompt.
        """
        pass

    def _embed_message_for_rag(self, uid: str, session_id: str, message_id: str, content: str) -> None:
        """
        TODO: next session
        Embeds message into ChromaDB for future RAG retrieval.
        """
        pass

    # ── Function Calling (scaffolded) ─────────────────────────────────────────

    def _get_challenge_tools(self) -> list:
        """
        TODO: next session
        Gemini tool definitions.
        Planned: recommend_challenge(type, reason)
        """
        pass

    def _handle_tool_calls(self, uid: str, tool_calls: list) -> str:
        """
        TODO: next session
        Executes tool calls returned by Gemini.
        """
        pass

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _assert_session_owned(self, uid: str, session_id: str) -> None:
        session = self.repo.get_session(uid, session_id)
        if session is None:
            raise AppException(status_code=404, message="Session not found.")

    def _to_session_data(self, doc: dict) -> SessionData:
        return SessionData(
            session_id=doc["session_id"],
            title=doc.get("title"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            message_count=doc["message_count"],
            summary=doc.get("summary"),
        )

    def _to_message_data(self, doc: dict) -> MessageData:
        return MessageData(
            message_id=doc["message_id"],
            session_id=doc["session_id"],
            sender=doc["sender"],
            content=doc["content"],
            timestamp=doc["timestamp"],
        )


def get_chat_service(repo: ChatRepository) -> ChatService:
    return ChatService(repo)