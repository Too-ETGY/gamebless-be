import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestLoggingMiddleware
from app.core.logging import setup_logging
from app.db.firebase import init_firebase
from app.api.v1.router import router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ───────────────────────────────────────────────────────────────
    logger.info("Starting Gamebless API initialization sequence...")

    # 1. Firebase
    init_firebase()
    logger.info("Firebase Admin SDK successfully initialized.")

    # 2. ChromaDB warm-up
    try:
        from app.db.vector_db import get_collection, embed_domain, BLOCKED_DOMAINS_COLLECTION

        logger.info("Loading ChromaDB client and fetching collection metadata...")
        collection = get_collection(BLOCKED_DOMAINS_COLLECTION)
        logger.info(f"ChromaDB collection '{BLOCKED_DOMAINS_COLLECTION}' found with {collection.count()} docs.")

        logger.info("Warming up ChromaDB HNSW index into system RAM...")

        # Use embed_domain (TF-IDF, 512-dim) — matches how the collection was built
        warmup_vector = embed_domain("warmup-ping.com")
        _ = collection.query(
            query_embeddings=[warmup_vector],
            n_results=1,
        )
        logger.info("ChromaDB index fully hydrated in RAM. Ready to intercept requests.")

    except Exception as e:
        logger.error(f"ChromaDB warm start skipped or failed: {e}", exc_info=True)

    yield

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    logger.info("Shutting down Gamebless API...")


app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>Gamebless API</h1>
    <p>Welcome to the Gamebless API! Visit <a href="/docs">here</a> for API documentation.</p>
    """


app.include_router(router, prefix="/api/v1")