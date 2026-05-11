from google.cloud.firestore_v1 import Client
import hashlib
import logging

logger = logging.getLogger(__name__)

BLOCKED_DOMAINS_COLLECTION = "blocked_domains"


class DomainRepository:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection(BLOCKED_DOMAINS_COLLECTION)

    def _hash_domain(self, domain: str) -> str:
        """Normalize and hash domain for use as document ID."""
        normalized = domain.lower().strip().removeprefix("https://").removeprefix("http://").removesuffix("/")
        return hashlib.md5(normalized.encode()).hexdigest()

    def get_by_domain(self, domain: str) -> dict | None:
        """Check if a domain exists in the blocked list."""
        doc_id = self._hash_domain(domain)
        doc = self.collection.document(doc_id).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict()}

    def create(self, domain: str, data: dict) -> dict:
        """Add a new domain to the collection."""
        doc_id = self._hash_domain(domain)
        ref = self.collection.document(doc_id)
        ref.set(data)
        return {"id": doc_id, **data}


def get_domain_repository(db: Client) -> DomainRepository:
    return DomainRepository(db)