from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum


class SenderType(str, Enum):
    USER = "user"
    AI = "ai"


class ChatSession(BaseModel):
    """
    Stored at: users/{uid}/chat_sessions/{session_id}
    """
    title: Optional[str] = None             # auto-generated from first message later
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    summary: Optional[str] = None           # filled when message_count exceeds threshold


class ChatMessage(BaseModel):
    """
    Stored at: users/{uid}/chat_sessions/{session_id}/messages/{message_id}
    """
    session_id: str
    sender: SenderType
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context_metadata: Optional[dict] = None     # for RAG tagging later