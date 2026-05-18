from datetime import date
from app.db.repositories.challenge_repo import ChallengeRepository
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.user_repo import UserRepository
from app.schemas.challenge import AllChallengesData, ChallengeTaskData, CompleteChallengeData, ChallengeHistoryData
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)


class ChallengeService:
    def __init__(self, challenge_repo: ChallengeRepository, progress_repo: ProgressRepository, user_repo: UserRepository):
        self.challenge_repo = challenge_repo
        self.progress_repo = progress_repo
        self.user_repo = user_repo

    def get_all(self, uid: str) -> AllChallengesData:
        today = date.today().isoformat()
        progress = self.progress_repo.get_by_date(uid, today)
        completed_today = set(progress.get("completed_challenges", []) if progress else [])
        challenges = self.challenge_repo.get_all()
        tasks = [ChallengeTaskData(**c, is_completed=c["task_id"] in completed_today) for c in challenges]
        return AllChallengesData(challenges=tasks, total=len(tasks))

    def complete(self, uid: str, task_id: str) -> CompleteChallengeData:
        task = self.challenge_repo.get_by_id(task_id)
        if task is None:
            raise AppException(status_code=404, message=f"Challenge '{task_id}' not found.")
        today = date.today().isoformat()
        if self.progress_repo.is_challenge_completed(uid, today, task_id):
            raise AppException(status_code=409, message="Challenge already completed today.")
        self.progress_repo.complete_challenge(uid, today, task_id, task["type"])
        total_points = self.user_repo.increment_points(uid, task["point_value"])
        logger.info(f"User {uid} completed {task_id} (+{task['point_value']} pts)")
        return CompleteChallengeData(task_id=task_id, points_awarded=task["point_value"], total_points=total_points)

    def get_history(self, uid: str) -> ChallengeHistoryData:
        all_challenges = {c["task_id"]: c for c in self.challenge_repo.get_all()}
        progress_docs = self.progress_repo.get_range(uid, "2000-01-01", date.today().isoformat())
        completed_ids = []
        for doc in progress_docs:
            completed_ids.extend(doc.get("completed_challenges", []))
        seen = set()
        unique_ids = [t for t in completed_ids if not (t in seen or seen.add(t))]
        completed_tasks = [ChallengeTaskData(**all_challenges[tid], is_completed=True) for tid in unique_ids if tid in all_challenges]
        user_doc = self.user_repo.get_by_id(uid)
        total_points = user_doc["account_stats"]["total_points"] if user_doc else 0
        return ChallengeHistoryData(completed_challenges=completed_tasks, total_points=total_points)