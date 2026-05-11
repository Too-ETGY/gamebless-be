from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse


# ── Requests ──────────────────────────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None    # if None, backend creates a new session


# ── Response Data ─────────────────────────────────────────────────────────────

class ChatMessageData(BaseModel):
    session_id: str
    message_id: str                     # auto-generated Firestore doc ID
    message: str
    sender: str                         # "user" | "ai"
    timestamp: datetime


class SendMessageData(BaseModel):
    session_id: str
    user_message: ChatMessageData
    # AI response is written to Firestore directly — Flutter listens via StreamBuilder
    # No ai_message here intentionally — frontend gets it via Firestore listener


# ── Composed Responses ────────────────────────────────────────────────────────

SendMessageResponse = ApiResponse[SendMessageData]