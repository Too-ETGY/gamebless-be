from google import genai

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client = None


def get_llm():
    """Return a configured Gemini client for scrape analysis in /report."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client