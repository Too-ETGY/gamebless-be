from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.chat import SenderType
from app.schemas.common import ApiResponse


# ── Requests ──────────────────────────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    content: str


# ── Response Data ─────────────────────────────────────────────────────────────

class SessionData(BaseModel):
    session_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int
    summary: Optional[str] = None


class MessageData(BaseModel):
    message_id: str
    session_id: str
    sender: SenderType
    content: str
    timestamp: datetime


class SendMessageData(BaseModel):
    user_message: MessageData
    ai_message: MessageData


class MessageListData(BaseModel):
    messages: List[MessageData]
    total: int
    has_summary: bool       # True if older messages were summarized


# ── Composed Responses ────────────────────────────────────────────────────────

SendMessageResponse = ApiResponse[SendMessageData]
SessionListResponse = ApiResponse[SessionData]
MessageListResponse = ApiResponse[MessageListData]