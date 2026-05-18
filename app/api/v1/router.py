from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, challenges, domains, chat, health

router = APIRouter()

router.include_router(health.router,                            tags=["Health"])
router.include_router(auth.router,       prefix="/auth",        tags=["Auth"])
router.include_router(users.router,      prefix="/users",       tags=["Users"])
router.include_router(challenges.router, prefix="/challenges",  tags=["Challenges"])
router.include_router(domains.router,    prefix="/domains",     tags=["Domains"])
router.include_router(chat.router,       prefix="/chat",        tags=["Chat"])