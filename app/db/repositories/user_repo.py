from google.cloud.firestore_v1 import Client
from app.models.user import UserProfile
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"


class UserRepository:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection(USERS_COLLECTION)

    def get_by_id(self, uid: str) -> dict | None:
        doc = self.collection.document(uid).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict()}

    def create(self, uid: str, email: str) -> dict:
        profile = UserProfile(email=email)
        data = {"profile": profile.model_dump()}
        self.collection.document(uid).set(data)
        logger.info(f"Created user: {uid}")
        return {"id": uid, **data}

    def update_profile(self, uid: str, fields: dict) -> dict:
        update_data = {f"profile.{k}": v for k, v in fields.items() if v is not None}
        self.collection.document(uid).update(update_data)
        return self.get_by_id(uid)

    def exists(self, uid: str) -> bool:
        return self.collection.document(uid).get().exists


def get_user_repository(db: Client) -> UserRepository:
    return UserRepository(db)