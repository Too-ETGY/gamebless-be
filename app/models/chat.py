from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum


class SenderType(str, Enum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"   # hidden from UI, used to trigger AI interventions


class ChatSession(BaseModel):
    """
    Stored at: users/{uid}/chat_sessions/{session_id}
    """
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    summary: Optional[str] = None
    is_active: bool = True              # False when session is archived after rotation


class ChatMessage(BaseModel):
    """
    Stored at: users/{uid}/chat_sessions/{session_id}/messages/{message_id}
    """
    session_id: str
    sender: SenderType
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reply_to: Optional[str] = None      # message_id this AI message is answering
    context_metadata: Optional[dict] = None