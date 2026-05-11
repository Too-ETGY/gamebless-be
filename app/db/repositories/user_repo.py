from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime, timezone
from app.models.user import UserProfile, AccountStats
import logging

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"


class UserRepository:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection(USERS_COLLECTION)

    def get_by_id(self, uid: str) -> dict | None:
        """Fetch user document by Firebase UID."""
        doc = self.collection.document(uid).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict()}
    
    def get_profile_by_id(self, uid: str) -> dict | None:
        """Fetch user profile by Firebase UID."""
        doc = self.collection.document(uid).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict().get("profile", {})}
    
    def get_account_stats_by_id(self, uid: str) -> dict | None:
        """Fetch user account stats by Firebase UID."""
        doc = self.collection.document(uid).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict().get("account_stats", {})}

    def upsert(self, uid: str, data: dict) -> dict:
        """
        Create or update user document.
        Uses merge=True so partial updates don't wipe existing fields.
        """
        ref = self.collection.document(uid)
        ref.set(data, merge=True)
        updated = ref.get()
        return {"id": updated.id, **updated.to_dict()}

    def update_profile(self, uid: str, profile_data: dict) -> dict:
        """Update only the profile sub-object."""
        ref = self.collection.document(uid)
        ref.update({"profile": profile_data})
        updated = ref.get()
        return {"id": updated.id, **updated.to_dict()}


def get_user_repository(db: Client) -> UserRepository:
    return UserRepository(db)