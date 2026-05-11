from pydantic import BaseModel
from typing import List


class ChallengeTask(BaseModel):
    task_id: str
    type: str                       # "video" | "article" | "exercise"
    content_url: str
    point_value: int
    description: str


class DailyChallenge(BaseModel):
    date: str                       # document ID format: "YYYY-MM-DD"
    tasks: List[ChallengeTask]