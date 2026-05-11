from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.progress import (
    ProgressResponse,
    TriggerAnalysisResponse,
    PointsBalanceResponse,
)
from app.core.response import success_response

router = APIRouter()


@router.get("", response_model=ProgressResponse)
async def get_progress(
    current_user: dict = Depends(get_current_user),
):
    """
    Returns full progress snapshot for the profile/progress screen.

    Includes:
    - account_stats (streak, total points, last access)
    - today's progress document (completed challenges, access tries, ai_summary)
    """
    # TODO: ProgressService.get_progress(uid)
    return success_response(data=None, message="Progress endpoint ready")


@router.post("/trigger-analysis", response_model=TriggerAnalysisResponse)
async def trigger_analysis(
    current_user: dict = Depends(get_current_user),
):
    """
    Manually triggers AI psychologist note generation.

    Flow:
    - Fetch recent user_progress documents (last 7 days)
    - Build prompt with behavioral data (streaks, access tries, completed challenges)
    - Call Gemini AI for summary/note
    - Save ai_summary to today's progress document
    - Return the generated note
    """
    # TODO: AIService.generate_progress_summary(uid)
    return success_response(data=None, message="Trigger analysis endpoint ready")


@router.get("/points", response_model=PointsBalanceResponse)
async def get_points_balance(
    current_user: dict = Depends(get_current_user),
):
    """
    Returns current points balance and streak.
    Lightweight — reads only account_stats from users document.
    """
    # TODO: ProgressService.get_points(uid)
    return success_response(data=None, message="Points balance endpoint ready")