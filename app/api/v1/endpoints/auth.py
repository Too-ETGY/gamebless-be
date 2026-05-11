from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.db.firebase import get_firestore
from app.db.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.schemas.auth import ProgressResponse, ProfileResponse, SyncRequest, SyncResponse
from app.core.response import success_response
from app.core.exceptions import AppException

router = APIRouter()


def get_auth_service() -> AuthService:
    db = get_firestore()
    repo = UserRepository(db)
    return AuthService(repo)


@router.post("/sync", response_model=SyncResponse)
async def sync_user(
    body: SyncRequest,
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """
    Called by frontend after Firebase login, and whenever user updates profile.

    Flow:
        1. Firebase handles login on frontend (Google OAuth etc.)
        2. Frontend gets Firebase ID token
        3. Frontend hits POST /auth/sync with token + user data
        4. Backend verifies token, upserts Firestore document
        5. Returns full user profile + stats

    First call  → creates user document

    Later calls → updates profile, preserves account_stats
    """
    uid = current_user["uid"]
    user_data = service.sync_user(uid, body)
    return success_response(data=user_data, message="User synced successfully")


# @router.get("/me", response_model=MeResponse)
# async def get_me(
#     current_user: dict = Depends(get_current_user),
#     service: AuthService = Depends(get_auth_service),
# ):
#     """
#     Returns the current user's profile and account stats.
#     Frontend hits this on app load to hydrate the profile screen.
#     """
#     uid = current_user["uid"]
#     user_data = service.get_me(uid)

#     if user_data is None:
#         raise AppException(
#             status_code=404,
#             message="User not found. Please sync first."
#         )

#     return success_response(data=user_data, message="User fetched successfully")

@router.get("/me", response_model=ProfileResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """
    Returns the current user's profile and account stats.
    Frontend hits this on app load to hydrate the profile screen.
    """
    uid = current_user["uid"]
    user_data = service.get_me(uid)

    if user_data is None:
        raise AppException(
            status_code=404,
            message="User not found. Please sync first."
        )

    return success_response(data=user_data, message="User fetched successfully")

# @router.get("/me/progress", response_model=ProgressResponse)
# async def get_progress(
#     current_user: dict = Depends(get_current_user),
#     service: AuthService = Depends(get_auth_service),
# ):
#     """
#     Returns the current user's account stats only.
#     Frontend hits this on app load to hydrate the profile screen.
#     """
#     uid = current_user["uid"]
#     user_data = service.get_me(uid)

#     if user_data is None:
#         raise AppException(
#             status_code=404,
#             message="User not found. Please sync first."
#         )

#     return success_response(data=user_data.account_stats, message="Progress fetched successfully")