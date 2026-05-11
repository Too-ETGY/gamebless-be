import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_app = None

def init_firebase() -> None:
    """Initialize Firebase app. Call once on startup in main.py."""
    global _app
    if _app is not None:
        return

    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        _app = firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        raise


def get_firestore():
    """Return Firestore client. Use as a FastAPI dependency."""
    return firestore.client()


def get_auth():
    """Return Firebase Auth client. Use as a FastAPI dependency."""
    return auth