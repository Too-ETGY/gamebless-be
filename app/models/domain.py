from pydantic import BaseModel
from typing import Optional

class BlockedDomain(BaseModel):
    domain: str
    reasoning: Optional[str] = None