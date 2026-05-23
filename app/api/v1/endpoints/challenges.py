from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.db.firebase import get_firestore
from app.db.repositories.challenge_repo import ChallengeRepository
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.user_repo import UserRepository
from app.services.challenge_service import ChallengeService
from app.schemas.challenge import ChallengeResponse, AllChallengesResponse, CompleteChallengeResponse, ChallengeHistoryResponse
from app.core.response import success_response

router = APIRouter()


def get_challenge_service() -> ChallengeService:
    db = get_firestore()
    return ChallengeService(ChallengeRepository(db), ProgressRepository(db), UserRepository(db))


@router.get("", response_model=AllChallengesResponse)
async def get_all_challenges(
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    """
    Returns all challenges marked with is_completed based on today's progress.
    """
    data = service.get_all(current_user["uid"])
    return success_response(data=data, message="Challenges fetched")


@router.get("/{task_id}/", response_model=ChallengeResponse)
async def get_a_challanges(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    data = service.get_challange_by_id(current_user["uid"], task_id)
    return success_response(data=data, message="Challenge {task_id} fethced")

@router.post("/{task_id}/complete", response_model=CompleteChallengeResponse)
async def complete_challenge(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    """
    Marks a challenge as completed.
    Deduplication check prevents point farming.
    Awards points to account_stats.total_points atomically.
    """
    data = service.complete(current_user["uid"], task_id)
    return success_response(data=data, message="Challenge completed")

@router.get("/history", response_model=ChallengeHistoryResponse)
async def get_challenge_history(
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    """
    All completed challenges across all time + total_points from account_stats.
    """
    data = service.get_history(current_user["uid"])
    return success_response(data=data, message="Challenge history fetched")