from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessage(BaseModel):
    session_id: str
    message: str
    sender: str                         # "user" | "ai"
    timestamp: datetime
    context_metadata: Optional[dict] = None     # for RAG tagging later