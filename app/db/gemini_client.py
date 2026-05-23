from google import genai

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client = None


def get_genai_client() -> genai.Client:
    """Singleton Gemini client using google-genai SDK."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini client initialized")
    return _client


def get_llm():
    """Return the Gemini client. Kept for backward compatibility with domain_service."""
    return get_genai_client()