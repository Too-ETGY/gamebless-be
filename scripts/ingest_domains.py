"""
One-time utility: reads domains.txt and ingests into ChromaDB.

Uses TF-IDF style character n-gram embeddings via scikit-learn — 
no API calls, no rate limits, no cost. Works great for domain name 
similarity since domains are short structured strings.

Usage:
    python -m scripts.ingest_domains

Place your government domain list at data/domains.txt (one domain per line).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

DOMAINS_FILE = "data/domains.txt"
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "blocked_domains"
BATCH_SIZE = 500    # no API = no rate limit, can go big


def normalize(domain: str) -> str:
    domain = domain.lower().strip()
    for prefix in ["https://", "http://", "www."]:
        domain = domain.removeprefix(prefix)
    return domain.split("/")[0]


def ingest():
    if not os.path.exists(DOMAINS_FILE):
        logger.error(f"File not found: {DOMAINS_FILE}")
        sys.exit(1)

    with open(DOMAINS_FILE, "r") as f:
        raw = [line.strip() for line in f if line.strip()]

    domains = [normalize(d) for d in raw]
    domains = list(dict.fromkeys(domains))
    logger.info(f"Loaded {len(domains)} unique domains")

    # ── Build embeddings locally with character n-grams ───────────────────────
    # char n-grams (2-4 chars) are great for domain names:
    # "poker99" → ["po", "ok", "ke", "er", "r9", "99", "pok", "oke", ...]
    # Similar domains (poker99 vs poker88) will have high cosine similarity
    logger.info("Building character n-gram embeddings (no API needed)...")
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        max_features=512,       # ChromaDB embedding dimension
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(domains)
    embeddings = matrix.toarray().tolist()
    logger.info(f"Embeddings built — shape: {len(embeddings)} x {len(embeddings[0])}")

    # ── Ingest into ChromaDB ──────────────────────────────────────────────────
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    existing_ids = set(collection.get()["ids"])
    to_ingest = [(d, e) for d, e in zip(domains, embeddings) if d not in existing_ids]
    logger.info(f"{len(to_ingest)} new domains to ingest ({len(existing_ids)} already stored)")

    if not to_ingest:
        logger.info("Nothing to ingest. Done.")
        return

    total = len(to_ingest)
    ingested = 0

    for i in range(0, total, BATCH_SIZE):
        batch = to_ingest[i:i + BATCH_SIZE]
        batch_domains = [d for d, _ in batch]
        batch_embeddings = [e for _, e in batch]

        try:
            collection.add(
                ids=batch_domains,
                embeddings=batch_embeddings,
                documents=batch_domains,
            )
            ingested += len(batch)
            logger.info(f"Progress: {ingested}/{total}")
        except Exception as e:
            logger.error(f"Batch failed at index {i}: {e}")
            continue

    logger.info(f"Done. {ingested} domains ingested.")
    logger.info(f"Collection now has {collection.count()} total documents.")

    # Save vectorizer so domain_service can use same embedding logic at query time
    import pickle
    with open("chroma_db/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    logger.info("Vectorizer saved to chroma_db/vectorizer.pkl")


if __name__ == "__main__":
    ingest()