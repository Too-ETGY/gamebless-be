import chromadb
import pickle
import os
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client = None
_collection = None
_vectorizer = None

COLLECTION_NAME = "blocked_domains"
VECTORIZER_PATH = "./chroma_db/vectorizer.pkl"


def get_chroma_client() -> chromadb.Client:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        logger.info(f"ChromaDB initialized at {settings.CHROMA_DB_PATH}")
    return _client


def get_domain_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection '{COLLECTION_NAME}' ready — {_collection.count()} docs")
    return _collection


def get_vectorizer():
    """Load the TF-IDF vectorizer saved during ingestion."""
    global _vectorizer
    if _vectorizer is None:
        if not os.path.exists(VECTORIZER_PATH):
            raise RuntimeError(
                "Vectorizer not found. Run scripts/ingest_domains.py first."
            )
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)
        logger.info("Vectorizer loaded from disk")
    return _vectorizer


def embed_domain(domain: str) -> list[float]:
    """Embed a single domain string using the same vectorizer used during ingestion."""
    vectorizer = get_vectorizer()
    vector = vectorizer.transform([domain])
    return vector.toarray()[0].tolist()