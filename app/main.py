from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestLoggingMiddleware
from app.core.logging import setup_logging
from app.db.firebase import init_firebase
from app.api.v1.router import router

setup_logging()  # Initialize logging configuration

# ── Firebase ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    init_firebase()  # Initialize Firebase on startup

    # try:
    #     # 1. Fetch your ChromaDB collection reference
    #     # (Replace this with whatever internal module method you use)
    #     from app.db.vector_db import chroma_client, COLLECTION_NAME
    #     collection = chroma_client.get_collection(COLLECTION_NAME)
        
        
    #     # 2. Trigger a dummy query to force ChromaDB to parse index files from disk
    #     # We query for an arbitrary domain string that won't disrupt anything.
    #     _ = collection.query(
    #         query_texts=["warmup_initialization_ping.com"],
    #         n_results=1
    #     )
        
        
    # except Exception as e:
    #     logger.error(f"Critical Error during ChromaDB warm start: {e}", exc_info=True)
        # Optional: Depending on competition rules, you can choose to fail the boot 
        # or let the API start with degraded initial performance.

    yield
    # Shutdown code (if needed) 

app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)

# Third-party middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)  # Register custom exception handlers

@app.get("/", response_class=HTMLResponse)
async def root():
    return """ 
    <h1>Gamebless API</h1>
    <p>Welcome to the Gamebless API! Visit <a href="/docs">here</a> for API documentation.</p>
    """

# Routes
app.include_router(router, prefix="/api/v1")