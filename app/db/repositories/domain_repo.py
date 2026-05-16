from google.cloud.firestore_v1 import Client
from app.models.domain import BlockedDomain
import hashlib
import logging

logger = logging.getLogger(__name__)

BLOCKED_DOMAINS_COLLECTION = "blocked_domains"


class DomainRepository:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection(BLOCKED_DOMAINS_COLLECTION)

    def _normalize(self, url: str) -> str:
        """Strip protocol, www, trailing slash. Returns clean domain string."""
        domain = url.lower().strip()
        for prefix in ["https://", "http://", "www."]:
            domain = domain.removeprefix(prefix)
        domain = domain.split("/")[0]   # remove any path
        return domain

    def _hash(self, domain: str) -> str:
        return hashlib.md5(domain.encode()).hexdigest()

    def get_by_url(self, url: str) -> dict | None:
        """Exact match lookup by normalized domain."""
        domain = self._normalize(url)
        doc = self.collection.document(self._hash(domain)).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **doc.to_dict()}

    def save(self, url: str, reasoning: str) -> dict:
        """Save a confirmed blocked domain into Firestore."""
        domain = self._normalize(url)
        doc_id = self._hash(domain)
        data = {
            "domain": domain,
            "reasoning": reasoning,
        }
        self.collection.document(doc_id).set(data)
        logger.info(f"Saved blocked domain: {domain} — {reasoning}")
        return {"id": doc_id, **data}

    def exists(self, url: str) -> bool:
        return self.get_by_url(url) is not None


def get_domain_repository(db: Client) -> DomainRepository:
    return DomainRepository(db)