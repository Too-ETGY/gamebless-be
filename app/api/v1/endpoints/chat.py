from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.db.firebase import get_firestore
from app.db.repositories.chat_repo import ChatRepository
from app.services.chat_service import ChatService
from app.schemas.chat import (
    SendMessageRequest,
    SendMessageResponse,
    SessionListResponse,
    MessageListResponse,
)
from app.schemas.common import ApiResponse
from app.core.response import success_response

router = APIRouter()


def get_chat_service() -> ChatService:
    return ChatService(ChatRepository(get_firestore()))


@router.get("/session", response_model=ApiResponse)
async def get_active_session(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Frontend calls this on app open.
    Returns the current active session (creates one if first time).
    Frontend stores the session_id and uses it for all message calls.
    User never sees or manages sessions manually.
    """
    session = service.get_or_create_active_session(current_user["uid"])
    return success_response(data=session, message="Active session ready")


@router.delete("/session", response_model=ApiResponse)
async def clear_session(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Clears the current chat history by creating a new session.
    """
    session = service.clear_active_session(current_user["uid"])
    return success_response(data=session, message="Session cleared")


@router.post("/session/messages", response_model=SendMessageResponse)
async def send_message(
    body: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Sends a user message and returns AI response.
    Uses the active session — frontend passes session_id from /chat/session.

    Flow:
    1. Validate session belongs to user
    2. Save user message
    3. Build context from recent history + summary
    4. Call Gemini with psychologist system prompt
    5. Save and return AI response
    6. Silently rotate session if threshold hit
    """
    session = service.get_or_create_active_session(current_user["uid"])
    data = service.send_message(current_user["uid"], session.session_id, body.content)
    return success_response(data=data, message="Message sent")


@router.get("/session/messages", response_model=MessageListResponse)
async def get_messages(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Returns full message history for the active session.
    Frontend calls this to restore conversation on app open.
    has_summary tells frontend whether older messages were summarized.
    """
    session = service.get_or_create_active_session(current_user["uid"])
    data = service.get_messages(current_user["uid"], session.session_id)
    return success_response(data=data, message="Messages fetched")