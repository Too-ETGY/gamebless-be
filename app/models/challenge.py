from enum import Enum
from typing import Optional
from pydantic import BaseModel

class ChallengeType(str, Enum):
    video = "video"
    article = "article"
    funfact = "funfact"

# document ID => task_id: str
class ChallengeTask(BaseModel):
    type: ChallengeType
    point_value: int
    title: str
    description: Optional[str]          # if article or funfact, this is the content. if video, it's optional
    image_url: Optional[str]            # cdn link
    video_url: Optional[str]            # if there is 
    article_url: Optional[str]          # completely optional, but just in case
    category: Optional[str]             # best practices only for funfact. but optionale by others. might be fine tho
    question: str
    options: list[str]
    correct_answers: int                # pointing at the options index