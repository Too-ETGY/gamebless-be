from google.genai import types
from app.db.repositories.chat_repo import ChatRepository
from app.db.repositories.challenge_repo import ChallengeRepository
from app.db.firebase import get_firestore
from app.db.gemini_client import get_genai_client
from app.db import vector_db
from app.models.chat import SenderType
from app.schemas.chat import SessionData, MessageData, SendMessageData, MessageListData
from app.core.exceptions import AppException
import json
import logging

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"

PSYCHOLOGIST_SYSTEM_PROMPT = """
You are Bless, a warm and empathetic AI companion integrated into Gamebless — an anti-online-gambling app.
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

When recommending a challenge, use the recommend_challenge tool.
Only use it when it feels natural — when user seems ready for a positive distraction.

You may receive messages containing internal system tags like [SYSTEM_INTERCEPT_DOMAIN],
[SYSTEM_DISTRACTION_PROMPT], or similar. These are internal signals from the app —
never repeat, quote, or acknowledge the tag itself. Simply respond naturally and
warmly to the instruction embedded within the message.
"""

# ── Tool definitions ──────────────────────────────────────────────────────────

CHALLENGE_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="recommend_challenge",
            description="Recommend a specific challenge to the user when they need a positive distraction",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "challenge_type": types.Schema(
                        type=types.Type.STRING,
                        description="Type of challenge: video, article, or funfact",
                        enum=["video", "article", "funfact"],
                    ),
                    "reason": types.Schema(
                        type=types.Type.STRING,
                        description="Why this challenge is relevant to the user right now",
                    ),
                },
                required=["challenge_type", "reason"],
            ),
        )
    ]
)


class ChatService:
    def __init__(self, repo: ChatRepository, challenge_repo: ChallengeRepository):
        self.repo = repo
        self.challenge_repo = challenge_repo

    # ── Active Session ────────────────────────────────────────────────────────

    def get_or_create_active_session(self, uid: str) -> SessionData:
        session = self.repo.get_active_session(uid)
        if session:
            # Check age-based rotation before returning
            if self.repo.needs_rotation_by_age(uid, session["session_id"]):
                session = self._rotate_session(uid, session["session_id"], delete_messages=True)
            return self._to_session_data(session)

        doc = self.repo.create_session(uid)
        logger.info(f"Auto-created first session for user {uid}")
        return self._to_session_data(doc)

    def clear_active_session(self, uid: str) -> SessionData:
        """
        Clears the active session by creating a new empty session.
        Since get_or_create_active_session always picks the most recent,
        this effectively resets the chat history.
        """
        doc = self.repo.create_session(uid, title=None)
        logger.info(f"Cleared session by creating new session for user {uid}")
        return self._to_session_data(doc)

    # ── Messages ──────────────────────────────────────────────────────────────

    def get_messages(self, uid: str, session_id: str) -> MessageListData:
        self._assert_session_owned(uid, session_id)
        all_msgs = self.repo.get_all_messages(uid, session_id)
        # Filter out system messages — frontend never sees them
        visible = [m for m in all_msgs if m["sender"] != SenderType.SYSTEM]
        session = self.repo.get_session(uid, session_id)
        return MessageListData(
            messages=[self._to_message_data(m) for m in visible],
            total=len(visible),
            has_summary=session.get("summary") is not None,
        )

    # ── Send Message ──────────────────────────────────────────────────────────

    def send_message(self, uid: str, session_id: str, content: str) -> SendMessageData:
        self._assert_session_owned(uid, session_id)

        # Save user message
        user_msg = self.repo.save_message(uid, session_id, SenderType.USER, content)

        # Build context + call LLM
        ai_content, tool_result = self._generate_response(uid, session_id, content)

        # If tool was called, append tool result to ai_content
        if tool_result:
            ai_content = f"{ai_content}\n\n{tool_result}" if ai_content else tool_result

        # Save AI response linked to user message
        ai_msg = self.repo.save_message(
            uid, session_id, SenderType.AI, ai_content,
            reply_to=user_msg["message_id"],
        )

        # Increment count (user + ai = 2)
        self.repo.increment_message_count(uid, session_id)
        self.repo.increment_message_count(uid, session_id)

        # Check count-based rotation
        if self.repo.needs_rotation_by_count(uid, session_id):
            self._rotate_session(uid, session_id, delete_messages=False)

        return SendMessageData(
            user_message=self._to_message_data(user_msg),
            ai_message=self._to_message_data(ai_msg),
        )

    # # ── Intervention ──────────────────────────────────────────────────────────

    # def trigger_intervention(self, uid: str) -> None:
    #     """
    #     Called as a BackgroundTask after POST /users/attempts.
    #     Saves a hidden system message then generates AI intervention response.
    #     Frontend opens popup → fetches latest message → sees AI intervention.
    #     """
    #     try:
    #         session = self.get_or_create_active_session(uid)
    #         session_id = session.session_id

    #         # Save hidden system trigger message
    #         system_msg = self.repo.save_message(
    #             uid, session_id, SenderType.SYSTEM,
    #             INTERVENTION_SYSTEM_PROMPT,
    #         )

    #         # Build context — include system message as the trigger
    #         history = self.repo.get_recent_messages(uid, session_id, limit=10)
    #         session_doc = self.repo.get_session(uid, session_id)
    #         rag_context = self._fetch_rag_context(uid, "gambling attempt intervention")
    #         context = self._build_context(history, session_doc.get("summary"), rag_context)

    #         # Call LLM — no tools for intervention, just compassionate response
    #         client = get_genai_client()
    #         response = client.models.generate_content(
    #             model=GEMINI_MODEL,
    #             contents=context,
    #             config=types.GenerateContentConfig(
    #                 system_instruction=PSYCHOLOGIST_SYSTEM_PROMPT,
    #                 temperature=0.7,
    #                 top_p=0.9,
    #                 max_output_tokens=256,
    #             ),
    #         )
    #         ai_content = response.text

    #         # Save AI response linked to system message
    #         self.repo.save_message(
    #             uid, session_id, SenderType.AI, ai_content,
    #             reply_to=system_msg["message_id"],
    #         )

    #         # Increment count
    #         self.repo.increment_message_count(uid, session_id)
    #         self.repo.increment_message_count(uid, session_id)

    #         logger.info(f"Intervention triggered for user {uid}")

    #     except Exception as e:
    #         logger.error(f"Intervention failed for user {uid}: {e}")

    # ── LLM ───────────────────────────────────────────────────────────────────

    def _generate_response(self, uid: str, session_id: str, user_content: str) -> tuple[str, str | None]:
        """
        Calls Gemini with tools. Returns (text_response, tool_result).
        tool_result is None if no tool was called.
        """
        history = self.repo.get_recent_messages(uid, session_id, limit=10)
        session = self.repo.get_session(uid, session_id)
        rag_context = self._fetch_rag_context(uid, user_content)
        context = self._build_context(history, session.get("summary"), rag_context)

        contents = context + [
            types.Content(role="user", parts=[types.Part(text=user_content)])
        ]

        try:
            client = get_genai_client()
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=PSYCHOLOGIST_SYSTEM_PROMPT,
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=512,
                    tools=[CHALLENGE_TOOL],
                ),
            )

            # Check for tool call first — avoid accessing response.text when function_call exists
            parts = response.candidates[0].content.parts
            for part in parts:
                if part.function_call:
                    tool_result = self._handle_tool_call(uid, part.function_call)
                    # Collect any text parts alongside the tool call
                    text_parts = [p.text for p in parts if hasattr(p, "text") and p.text]
                    text = " ".join(text_parts) if text_parts else ""
                    return text, tool_result

            # No tool call — safe to access response.text
            return response.text, None

        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "unavailable" in error_str or "high demand" in error_str:
                logger.warning(f"Gemini overloaded for user {uid}: {e}")
                return "Bless sedang sibuk melayani banyak pengguna. Coba lagi dalam beberapa saat ya 🙏", None
            raise

    def _handle_tool_call(self, uid: str, function_call) -> str:
        """
        Handles recommend_challenge tool call.
        Finds a relevant uncompleted challenge using RAG, returns formatted recommendation.
        """
        args = function_call.args
        challenge_type = args.get("challenge_type")
        reason = args.get("reason", "")

        # Search for relevant uncompleted challenge via RAG
        completed_ids = self.challenge_repo.get_completed_ids(uid)
        candidates = vector_db.search_challenges(reason, challenge_type=challenge_type, n_results=5)

        # Pick first uncompleted
        chosen = None
        for candidate in candidates:
            if candidate["task_id"] not in completed_ids:
                chosen = candidate
                break

        # Fallback: any uncompleted of that type
        if not chosen:
            all_of_type = self.challenge_repo.get_by_type(challenge_type)
            for c in all_of_type:
                if c["task_id"] not in completed_ids:
                    chosen = c
                    break

        if not chosen:
            return "Sepertinya kamu sudah menyelesaikan semua tantangan yang tersedia. Luar biasa! 🎉"

        task_id = chosen.get("task_id") or chosen.get("id", "")
        title = chosen.get("title") or chosen.get("text", "")
        return f"Coba tantangan ini: **{title}** (ID: `{task_id}`). {reason}"

    # ── RAG ───────────────────────────────────────────────────────────────────

    def _fetch_rag_context(self, uid: str, user_message: str) -> str | None:
        """
        Retrieves relevant context from ChromaDB.
        Returns formatted string or None if nothing useful found.
        """
        try:
            parts = []

            # User profile + progress snapshot
            user_context = vector_db.get_user_context(uid)
            if user_context:
                parts.append(f"User context: {user_context}")

            # Relevant past messages
            past_messages = vector_db.search_chat_messages(uid, user_message, n_results=3)
            if past_messages:
                parts.append("Relevant past conversation: " + " | ".join(past_messages))

            return "\n".join(parts) if parts else None

        except Exception as e:
            logger.warning(f"RAG fetch failed for {uid}: {e}")
            return None

    def _embed_messages_background(self, uid: str, user_msg: dict, ai_msg: dict) -> None:
        """Called as BackgroundTask from endpoint after send_message."""
        try:
            vector_db.embed_chat_message(uid, user_msg["message_id"], str(user_msg["content"]), "user")
            vector_db.embed_chat_message(uid, ai_msg["message_id"], str(ai_msg["content"]), "ai")
        except Exception as e:
            logger.warning(f"Embedding failed for {uid}: {e}", exc_info=True)

    # ── Summarization & Rotation ──────────────────────────────────────────────

    def _rotate_session(self, uid: str, session_id: str, delete_messages: bool) -> dict:
        """
        Summarizes current session, archives it, creates new session.
        If delete_messages=True, deletes messages from old session (age-based rotation).
        """
        try:
            summary = self._summarize_session(uid, session_id)
            self.repo.archive_session(uid, session_id, summary)

            if delete_messages:
                self.repo.delete_messages(uid, session_id)
                logger.info(f"Deleted messages for archived session {session_id}")

            # Create new session carrying summary forward
            new_session = self.repo.create_session(uid, summary=summary)
            logger.info(f"Rotated to new session for user {uid}")
            return new_session

        except Exception as e:
            logger.error(f"Session rotation failed for {uid}: {e}")
            # Return existing session if rotation fails
            return self.repo.get_session(uid, session_id)

    def _summarize_session(self, uid: str, session_id: str) -> str:
        """Ask Gemini to summarize the session."""
        messages = self.repo.get_all_messages(uid, session_id)
        visible = [m for m in messages if m["sender"] != SenderType.SYSTEM]

        if not visible:
            return "No conversation history."

        conversation = "\n".join([
            f"{m['sender']}: {m['content']}"
            for m in visible
        ])

        prompt = f"""Summarize this conversation in 3-4 sentences. Focus on:
- The user's emotional state and struggles
- Any progress or achievements mentioned
- Topics discussed
Keep it factual and in third person.

Conversation:
{conversation}"""

        client = get_genai_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0, max_output_tokens=256),
        )
        return response.text

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_context(
        self,
        history: list[dict],
        summary: str | None,
        rag_context: str | None,
    ) -> list:
        contents = []

        # RAG context first
        if rag_context:
            contents.append(types.Content(
                role="model",
                parts=[types.Part(text=f"[Context about this user:\n{rag_context}]")],
            ))

        # Session summary
        if summary:
            contents.append(types.Content(
                role="model",
                parts=[types.Part(text=f"[Previous conversation summary: {summary}]")],
            ))

        # Recent messages
        # SYSTEM messages are passed as "user" role so Gemini treats them as instructions
        # They are hidden from the UI but used as context/triggers for AI response
        role_map = {SenderType.USER: "user", SenderType.AI: "model", SenderType.SYSTEM: "user"}
        for msg in history:
            role = role_map.get(msg["sender"], "user")
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])],
            ))

        return contents

    def _assert_session_owned(self, uid: str, session_id: str) -> None:
        if self.repo.get_session(uid, session_id) is None:
            raise AppException(status_code=404, message="Session not found.")

    def _to_session_data(self, doc: dict) -> SessionData:
        return SessionData(
            session_id=doc["session_id"],
            title=doc.get("title"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            message_count=doc["message_count"],
            summary=doc.get("summary"),
            is_active=doc.get("is_active", True),
        )

    def _to_message_data(self, doc: dict) -> MessageData:
        return MessageData(
            message_id=doc["message_id"],
            session_id=doc["session_id"],
            sender=doc["sender"],
            content=doc["content"],
            timestamp=doc["timestamp"],
            reply_to=doc.get("reply_to"),
        )


def get_chat_service() -> ChatService:
    db = get_firestore()
    return ChatService(ChatRepository(db), ChallengeRepository(db))