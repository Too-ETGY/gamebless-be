from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.challenge import (
    DailyChallengesResponse,
    AllChallengesResponse,
    CompleteTaskResponse,
)
from app.core.response import success_response

router = APIRouter()


@router.get("/daily", response_model=DailyChallengesResponse)
async def get_daily_challenges(
    # current_user: dict = Depends(get_current_user),
):
    """
    Returns today's challenge tasks (video, article, exercise).
    Document ID in Firestore is today's date: "YYYY-MM-DD".
    """
    # TODO: ChallengeService.get_daily()
    return success_response(data=None, message="Daily challenges endpoint ready")


@router.get("", response_model=AllChallengesResponse)
async def get_all_challenges(
    # current_user: dict = Depends(get_current_user),
):
    """
    Returns all available challenge documents.
    Useful for browsing past or upcoming challenges.
    """
    # TODO: ChallengeService.get_all()
    return success_response(data=None, message="All challenges endpoint ready")


@router.post("/{task_id}/complete", response_model=CompleteTaskResponse)
async def complete_challenge(
    task_id: str,
    # current_user: dict = Depends(get_current_user),
):
    """
    Marks a challenge task as completed.

    Flow:
    - Verify task exists in today's challenges
    - Check not already completed by this user today
    - Add task_id to user_progress.completed_challenges
    - Add point_value to today_points_earned and account_stats.total_points
    """
    # TODO: ChallengeService.complete(task_id, uid)
    return success_response(data=None, message="Complete challenge endpoint ready")