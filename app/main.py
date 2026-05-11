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