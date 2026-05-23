from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.db.firebase import get_firestore
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.progress_repo import ProgressRepository
from app.db.repositories.challenge_repo import ChallengeRepository
from app.services.user_service import UserService
from app.schemas.auth import SyncRequest, SyncResponse
from app.core.response import success_response

router = APIRouter()


def get_user_service() -> UserService:
    db = get_firestore()
    return UserService(UserRepository(db), ProgressRepository(db), ChallengeRepository(db))


@router.post("/sync", response_model=SyncResponse)
async def sync_user(
    body: SyncRequest,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """
    Called by Firebase on first login only.
    Creates a minimal user document — everything except email and join_date is null/0.
    If user already exists, returns existing profile without overwriting.
    """
    profile = service.sync(current_user["uid"], body.email)
    return success_response(data=profile, message="User synced successfully")