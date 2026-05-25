import chromadb
import pickle
import os
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client = None
_vectorizer = None
_embedding_model = None

# ── Collection names ──────────────────────────────────────────────────────────
BLOCKED_DOMAINS_COLLECTION = "blocked_domains"
CHAT_COLLECTION = "chat_messages"
CHALLENGE_COLLECTION = "challenges"
USER_CONTEXT_COLLECTION = "user_context"

VECTORIZER_PATH = "./chroma_db/vectorizer.pkl"


# ── Client ────────────────────────────────────────────────────────────────────

def get_chroma_client() -> chromadb.Client:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        logger.info(f"ChromaDB initialized at {settings.CHROMA_DB_PATH}")
    return _client

def get_collection(name: str) -> chromadb.Collection:
    client = get_chroma_client()
    try:
        return client.get_collection(name=name)
    except Exception:
        return client.create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )


# ── Domain: TF-IDF vectorizer (no API, used for blocked_domains) ──────────────

def get_domain_collection() -> chromadb.Collection:
    global _collection_domain
    _collection_domain = get_collection(BLOCKED_DOMAINS_COLLECTION)
    logger.info(f"ChromaDB collection '{BLOCKED_DOMAINS_COLLECTION}' ready — {_collection_domain.count()} docs")
    return _collection_domain


def get_vectorizer():
    """Load the TF-IDF vectorizer saved during ingestion."""
    global _vectorizer
    if _vectorizer is None:
        if not os.path.exists(VECTORIZER_PATH):
            raise RuntimeError("Vectorizer not found. Run scripts/ingest_domains.py first.")
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)
        logger.info("Vectorizer loaded from disk")
    return _vectorizer


def embed_domain(domain: str) -> list[float]:
    """Embed domain string using TF-IDF vectorizer. Fast, no API needed."""
    vectorizer = get_vectorizer()
    vector = vectorizer.transform([domain])
    return vector.toarray()[0].tolist()


# ── Chat/Challenges: sentence-transformers (multilingual, free) ───────────────

def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        logger.info("Sentence-transformer embedding model loaded")
    return _embedding_model


def embed_text(text: str) -> list[float]:
    """Embed text using multilingual sentence-transformers. Supports Bahasa Indonesia + English."""
    model = _get_embedding_model()
    return model.encode(text).tolist()


# ── Chat Messages ─────────────────────────────────────────────────────────────

def embed_chat_message(uid: str, message_id: str, content: str, sender: str) -> None:
    collection = get_collection(CHAT_COLLECTION)
    collection.upsert(
        ids=[message_id],
        embeddings=[embed_text(content)],
        documents=[content],
        metadatas=[{"uid": uid, "sender": sender}],
    )


def search_chat_messages(uid: str, query: str, n_results: int = 3) -> list[str]:
    collection = get_collection(CHAT_COLLECTION)
    if collection.count() == 0:
        return []
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=n_results,
        where={"uid": uid},
        include=["documents"],
    )
    return results.get("documents", [[]])[0]


# ── User Context ──────────────────────────────────────────────────────────────

def upsert_user_context(uid: str, context_text: str) -> None:
    """One document per user — upsert replaces on profile/progress update."""
    collection = get_collection(USER_CONTEXT_COLLECTION)
    collection.upsert(
        ids=[uid],
        embeddings=[embed_text(context_text)],
        documents=[context_text],
        metadatas=[{"uid": uid}],
    )


def get_user_context(uid: str) -> str | None:
    collection = get_collection(USER_CONTEXT_COLLECTION)
    try:
        result = collection.get(ids=[uid], include=["documents"])
        docs = result.get("documents", [])
        return docs[0] if docs else None
    except Exception:
        return None


# ── Challenges ────────────────────────────────────────────────────────────────

def embed_challenge(task_id: str, challenge_type: str, title: str, description: str | None) -> None:
    """Embed challenge for recommendation RAG. Call once per challenge (or on update)."""
    collection = get_collection(CHALLENGE_COLLECTION)
    text = f"{title}. {description or ''}"
    collection.upsert(
        ids=[task_id],
        embeddings=[embed_text(text)],
        documents=[text],
        metadatas=[{"type": challenge_type}],
    )


def search_challenges(query: str, challenge_type: str | None = None, n_results: int = 5) -> list[dict]:
    collection = get_collection(CHALLENGE_COLLECTION)
    if collection.count() == 0:
        return []
    where = {"type": challenge_type} if challenge_type else None
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "ids"],
    )
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return [{"task_id": i, "text": d, "type": m.get("type")} for i, d, m in zip(ids, docs, metas)]