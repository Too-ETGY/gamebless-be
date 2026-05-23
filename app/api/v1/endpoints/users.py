from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.db.firebase import get_firestore
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.challenge_repo import ChallengeRepository
from app.services.user_service import UserService
from app.services.progress_service import ProgressService
from app.schemas.user import MeResponse, UpdateProfileRequest, UpdateProfileResponse, AttemptRequest
from app.schemas.progress import AttemptResponse, ProgressReportResponse
from app.core.response import success_response

router = APIRouter()


def get_user_service() -> UserService:
    db = get_firestore()
    return UserService(UserRepository(db), ProgressRepository(db), ChallengeRepository(db))


def get_progress_service() -> ProgressService:
    db = get_firestore()
    return ProgressService(ProgressRepository(db), UserRepository(db), ChallengeRepository(db))


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """
    GET profile + account_stats in one Firestore read.
    Frontend hits this on app launch to render points and streak instantly.
    """
    me = service.get_me(current_user["uid"])
    return success_response(data=me, message="User fetched successfully")


@router.put("/me", response_model=UpdateProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """
    PUT update profile fields only.
    Only fields provided in the body are updated — others are untouched.
    """
    fields = body.model_dump(exclude_none=True)
    profile = service.update_profile(current_user["uid"], fields)
    return success_response(data=profile, message="Profile updated successfully")


@router.post("/attempts", response_model=AttemptResponse)
async def record_attempt(
    body: AttemptRequest,
    current_user: dict = Depends(get_current_user),
    service: ProgressService = Depends(get_progress_service),
):
    """
    Called by frontend when /domains/check returns is_blocked=true.
    Increments access_attempts_count on today's progress doc.
    Resets current_streak to 0 on first attempt of the day.
    """
    result = service.record_attempt(current_user["uid"])
    return success_response(data=result, message="Attempt recorded")


@router.get("/progress-report", response_model=ProgressReportResponse)
async def get_progress_report(
    current_user: dict = Depends(get_current_user),
    service: ProgressService = Depends(get_progress_service),
):
    """
    Full progress report from join_date (capped at MAX_REPORT_DAYS).
    Computes highest_streak via linear scan — no extra DB field needed.
    is_capped and cap_days are returned so frontend can show a notice.
    """
    report = service.get_progress_report(current_user["uid"])
    return success_response(data=report, message="Progress report fetched")