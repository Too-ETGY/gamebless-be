from fastapi import APIRouter, Depends, BackgroundTasks
from app.dependencies import get_current_user
from app.services.chat_service import ChatService, get_chat_service
from app.schemas.chat import (
    SendMessageRequest,
    SendMessageResponse,
    SessionListResponse,
    MessageListResponse,
)
from app.schemas.common import ApiResponse
from app.core.response import success_response

router = APIRouter()


@router.get("/session", response_model=ApiResponse)
async def get_active_session(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Frontend calls on app open.
    Returns active session — creates one if first time.
    Handles age-based rotation silently.
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
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Send message, get AI response with optional challenge recommendation.
    Embeds messages for RAG in background.
    """
    uid = current_user["uid"]
    session = service.get_or_create_active_session(uid)
    data = service.send_message(uid, session.session_id, body.content)

    # Embed messages for RAG in background
    background_tasks.add_task(
        service._embed_messages_background,
        uid,
        data.user_message.model_dump(),
        data.ai_message.model_dump(),
    )

    return success_response(data=data, message="Message sent")


@router.get("/session/messages", response_model=MessageListResponse)
async def get_messages(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Returns visible message history (system messages excluded).
    Frontend calls on app open to restore conversation.
    """
    uid = current_user["uid"]
    session = service.get_or_create_active_session(uid)
    data = service.get_messages(uid, session.session_id)
    return success_response(data=data, message="Messages fetched")