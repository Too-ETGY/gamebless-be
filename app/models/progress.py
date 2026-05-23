from datetime import datetime, timezone
from pydantic import BaseModel, Field

# document ID format: "YYYY-MM-DD"
# means: if user is accessing a judol site, this document is created with that date.. 
class UserProgress(BaseModel):
    attempt_count: int
    last_attempt_at: datetime = Field(default_factory=lambda: (datetime.now(timezone.utc)))  