from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.db.firebase import get_firestore
from app.db.repositories.challenge_repo import ChallengeRepository
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.user_repo import UserRepository
from app.services.challenge_service import ChallengeService
from app.schemas.challenge import (
    AllChallengesResponse,
    ChallengeTaskResponse,
    CompleteChallengeResponse,
    ChallengeHistoryResponse,
)
from app.core.response import success_response

router = APIRouter()


def get_challenge_service() -> ChallengeService:
    db = get_firestore()
    return ChallengeService(ChallengeRepository(db))


@router.get("", response_model=AllChallengesResponse)
async def get_all_challenges(
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    data = service.get_all(current_user["uid"])
    return success_response(data=data, message="Challenges fetched")


@router.get("/history", response_model=ChallengeHistoryResponse)
async def get_challenge_history(
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    data = service.get_history(current_user["uid"])
    return success_response(data=data, message="Challenge history fetched")


@router.get("/type/{challenge_type}", response_model=AllChallengesResponse)
async def get_challenges_by_type(
    challenge_type: str,
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    """Returns challenges filtered by type: video | article | funfact"""
    data = service.get_by_type(current_user["uid"], challenge_type)
    return success_response(data=data, message=f"{challenge_type} challenges fetched")


@router.get("/{task_id}", response_model=ChallengeTaskResponse)
async def get_challenge_by_id(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    """Returns a single challenge with is_completed status."""
    data = service.get_by_id(current_user["uid"], task_id)
    return success_response(data=data, message="Challenge fetched")


@router.post("/{task_id}/complete", response_model=CompleteChallengeResponse)
async def complete_challenge(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    service: ChallengeService = Depends(get_challenge_service),
):
    data = service.complete(current_user["uid"], task_id)
    return success_response(data=data, message="Challenge completed")