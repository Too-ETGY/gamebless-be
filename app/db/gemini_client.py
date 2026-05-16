import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True


def get_llm():
    """Return Gemini Flash — used only for scrape analysis in /report."""
    _ensure_configured()
    return genai.GenerativeModel("gemini-2.5-flash")