from fastapi import APIRouter, Depends, BackgroundTasks
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
from app.db import vector_db

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
    me = service.get_me(current_user["uid"])
    return success_response(data=me, message="User fetched successfully")


@router.put("/me", response_model=UpdateProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    uid = current_user["uid"]
    fields = body.model_dump(exclude_none=True)
    profile = service.update_profile(uid, fields)

    # Update user context embedding in background
    background_tasks.add_task(_update_user_context_embedding, uid, service)

    return success_response(data=profile, message="Profile updated successfully")


@router.post("/attempts", response_model=AttemptResponse)
async def record_attempt(
    body: AttemptRequest,
    current_user: dict = Depends(get_current_user),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """
    Called when /domains/check returns is_blocked=true.
    Records attempt + triggers AI intervention message in background.
    Frontend opens popup → fetches /chat/session/messages → latest is AI intervention.
    """
    uid = current_user["uid"]
    result = progress_service.record_attempt(uid)

    return success_response(data=result, message="Attempt recorded")


@router.get("/progress-report", response_model=ProgressReportResponse)
async def get_progress_report(
    current_user: dict = Depends(get_current_user),
    service: ProgressService = Depends(get_progress_service),
):
    report = service.get_progress_report(current_user["uid"])
    return success_response(data=report, message="Progress report fetched")


# ── Background helpers ────────────────────────────────────────────────────────

async def _update_user_context_embedding(uid: str, service: UserService) -> None:
    """
    Rebuilds user context embedding after profile update.
    Only called from PUT /users/me — not on sync (profile is empty then).
    """
    try:
        doc = service.user_repo.get_by_id(uid)
        if not doc:
            return
        profile = doc["profile"]
        join_date = profile.get("join_date")
        if hasattr(join_date, "date"):
            join_date_str = join_date.date().isoformat()
        elif join_date:
            join_date_str = str(join_date)[:10]
        else:
            join_date_str = "unknown"
 
        context_text = (
            f"User profile: "
            f"username={profile.get('username')}, "
            f"occupation={profile.get('occupation')}, "
            f"gender={profile.get('gender')}, "
            f"joined={join_date_str}"
        )
        vector_db.upsert_user_context(uid, context_text)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"User context embedding failed: {e}")