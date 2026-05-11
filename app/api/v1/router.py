from fastapi import APIRouter
from app.api.v1.endpoints import health , auth, domains, challenges, progress, chat

router = APIRouter()

router.include_router(health.router)
# need test from fontend
router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# working on it
router.include_router(domains.router,    prefix="/domains",     tags=["Domains"])
router.include_router(challenges.router, prefix="/challenges",  tags=["Challenges"])
router.include_router(progress.router,   prefix="/progress",    tags=["Progress"])
router.include_router(chat.router,       prefix="/chat",        tags=["Chat"])