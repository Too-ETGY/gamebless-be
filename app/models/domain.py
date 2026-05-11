from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BlockedDomain(BaseModel):
    domain: str
    status: str                     # "verified" | "pending_review" | "officially_blocked"
    reasoning: Optional[str] = None
    created_at: Optional[datetime] = None