"""
One-time utility: reads challenges from Firestore and embeds them into ChromaDB.
Run this after adding new challenges via Firestore console.

Usage:
    python -m scripts.ingest_challenges
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.vector_db import embed_challenge, get_collection, CHALLENGE_COLLECTION
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def ingest():
    # Init Firebase
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    docs = db.collection("challenges").stream()
    challenges = [{"task_id": doc.id, **doc.to_dict()} for doc in docs]

    if not challenges:
        logger.warning("No challenges found in Firestore. Add some first.")
        return

    logger.info(f"Found {len(challenges)} challenges in Firestore")

    collection = get_collection(CHALLENGE_COLLECTION)
    existing_ids = set(collection.get()["ids"])

    to_ingest = [c for c in challenges if c["task_id"] not in existing_ids]
    logger.info(f"{len(to_ingest)} new challenges to embed ({len(existing_ids)} already stored)")

    if not to_ingest:
        logger.info("Nothing to ingest. Done.")
        return

    for c in to_ingest:
        try:
            embed_challenge(
                task_id=c["task_id"],
                challenge_type=c.get("type", ""),
                title=c.get("title", ""),
                description=c.get("description"),
            )
            logger.info(f"Embedded: {c['task_id']} ({c.get('type')}) — {c.get('title')}")
        except Exception as e:
            logger.error(f"Failed to embed {c['task_id']}: {e}")

    logger.info(f"Done. Collection now has {collection.count()} challenges.")


if __name__ == "__main__":
    ingest()