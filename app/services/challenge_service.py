from datetime import date
from app.db.repositories.challenge_repo import ChallengeRepository
from app.schemas.challenge import (
    AllChallengesData, ChallengeTaskData, CompleteChallengeData,
    ChallengeHistoryData, CompletedChallengeData,
)
from app.models.challenge import ChallengeType
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)


class ChallengeService:
    def __init__(self, challenge_repo: ChallengeRepository):
        self.challenge_repo = challenge_repo

    def get_all(self, uid: str) -> AllChallengesData:
        challenges = self.challenge_repo.get_all()
        completed_ids = self.challenge_repo.get_completed_ids(uid)
        tasks = [
            self._to_task_data(c, is_completed=(c.get("task_id") in completed_ids))
            for c in challenges
        ]
        return AllChallengesData(challenges=tasks, total=len(tasks))

    def get_by_id(self, uid: str, task_id: str) -> ChallengeTaskData:
        task = self.challenge_repo.get_by_id(task_id)
        if task is None:
            raise AppException(status_code=404, message=f"Challenge '{task_id}' not found.")
        is_completed = self.challenge_repo.is_completed(uid, task_id)
        return self._to_task_data(task, is_completed=is_completed)

    def get_by_type(self, uid: str, challenge_type: ChallengeType) -> AllChallengesData:
        challenges = self.challenge_repo.get_by_type(challenge_type)
        completed_ids = self.challenge_repo.get_completed_ids(uid)
        tasks = [
            self._to_task_data(c, is_completed=(c.get("task_id") in completed_ids))
            for c in challenges
        ]
        return AllChallengesData(challenges=tasks, total=len(tasks))

    def _to_task_data(self, c: dict, is_completed: bool) -> ChallengeTaskData:
        # Normalize Firestore document dict to the fields expected by ChallengeTaskData
        data = {
            "task_id": c.get("task_id"),
            "type": c.get("type"),
            "point_value": c.get("point_value", 0),
            "title": c.get("title", ""),
            "description": c.get("description", None),
            "image_url": c.get("image_url", None),
            "video_url": c.get("video_url", None),
            "article_url": c.get("article_url", None),
            "category": c.get("category", None),
            "question": c.get("question", ""),
            "options": c.get("options", []) or [],
            "correct_answers": c.get("correct_answers", 0),
            "is_completed": is_completed,
        }
        return ChallengeTaskData(**data)

    def complete(self, uid: str, task_id: str) -> CompleteChallengeData:
        task = self.challenge_repo.get_by_id(task_id)
        if task is None:
            raise AppException(status_code=404, message=f"Challenge '{task_id}' not found.")

        if self.challenge_repo.is_completed(uid, task_id):
            raise AppException(status_code=409, message="Challenge already completed.")

        self.challenge_repo.save_completed(uid, task_id, task["type"], task["point_value"])

        # total_points computed from subcollection
        completed = self.challenge_repo.get_completed(uid)
        total_points = sum(c.get("points", 0) for c in completed)

        logger.info(f"User {uid} completed {task_id} (+{task['point_value']} pts)")
        return CompleteChallengeData(
            task_id=task_id,
            points_awarded=task["point_value"],
            total_points=total_points,
        )

    def get_history(self, uid: str) -> ChallengeHistoryData:
        """Option B — returns only completed challenge data, no full task details."""
        completed = self.challenge_repo.get_completed(uid)
        total_points = sum(c.get("points", 0) for c in completed)
        items = [
            CompletedChallengeData(
                task_id=c["task_id"],
                type=c["type"],
                points_awarded=c["points"],
                completed_at=c["completed_at"],
            )
            for c in completed
        ]
        return ChallengeHistoryData(
            completed_challenges=items,
            total_points=total_points,
            total_completed=len(items),
        )


def get_challenge_service(challenge_repo: ChallengeRepository) -> ChallengeService:
    return ChallengeService(challenge_repo)