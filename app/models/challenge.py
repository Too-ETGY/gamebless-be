from enum import Enum
from pydantic import BaseModel

class ChallengeType(str, Enum):
    video = "video"
    article = "article"
    funfact = "funfact"

class ChallengeTask(BaseModel):
    task_id: str
    type: ChallengeType
    content_url: str = None
    point_value: int
    question: str = None