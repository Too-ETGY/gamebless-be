from firebase_admin import auth
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)

def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token and return decoded claims.
    Raises AppException if token is invalid or expired.
    """
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except auth.ExpiredIdTokenError:
        raise AppException(status_code=401, message="Token has expired")
    except auth.InvalidIdTokenError:
        raise AppException(status_code=401, message="Invalid token")
    except auth.RevokedIdTokenError:
        raise AppException(status_code=401, message="Token has been revoked")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise AppException(status_code=401, message="Authentication failed")