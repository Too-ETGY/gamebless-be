import json
import logging
from app.db.repositories.domain_repo import DomainRepository
from app.db.vector_db import get_domain_collection, embed_domain
from app.db.gemini_client import get_llm
from app.utils.scraper import scrape_domain_signals

logger = logging.getLogger(__name__)

# ── Thresholds ────────────────────────────────────────────────────────────────
# ChromaDB cosine distance: 0.0 = identical, 1.0 = completely different
# So we flip it: similarity = 1 - distance
# Report: save if similarity >= 0.70 (skip scraping, high confidence)
# Check:  block if similarity >= 0.85 (stricter, no scraping fallback)

REPORT_SIMILARITY_THRESHOLD = 0.70
CHECK_SIMILARITY_THRESHOLD = 0.80


def _normalize_url(url: str) -> str:
    """Strip protocol, www, trailing slash."""
    domain = url.lower().strip()
    for prefix in ["https://", "http://", "www."]:
        domain = domain.removeprefix(prefix)
    return domain.split("/")[0]


def _vector_search(domain: str) -> float:
    """
    Embed domain string and query ChromaDB.
    Returns best similarity score (0.0 - 1.0). 0.0 if collection is empty.
    """
    collection = get_domain_collection()

    if collection.count() == 0:
        logger.warning("ChromaDB collection is empty — run scripts/ingest_domains.py first")
        return 0.0

    embedding = embed_domain(domain)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=1,
        include=["distances"],
    )

    distances = results.get("distances", [[]])[0]
    if not distances:
        return 0.0

    # Cosine distance → similarity
    similarity = 1 - distances[0]
    logger.info(f"Vector search '{domain}' → similarity {similarity:.3f}")
    return similarity


def _llm_analyze(signals: dict) -> dict:
    """
    Send scraped signals to Gemini for gambling site determination.
    Returns { blocked: bool, reasoning: str }
    """
    model = get_llm()

    prompt = f"""
You are analyzing a website to determine if it is an online gambling site ("judol" / judi online).

Here is the extracted content from the website:

Title: {signals.get('title', 'N/A')}
Meta Description: {signals.get('meta_description', 'N/A')}
Headings (H1/H2): {signals.get('headings', 'N/A')}
Navigation Links: {signals.get('navigation', 'N/A')}
Footer Text: {signals.get('footer', 'N/A')}
Button Text: {signals.get('buttons', 'N/A')}

Common gambling indicators in Indonesian sites: slot, togel, casino, poker, betting, taruhan, deposit, withdraw, bonus, jackpot, RTP, zeus, petir, 999, provider (Pragmatic, PG Soft, Habanero).

Respond ONLY with valid JSON, no markdown, no explanation outside the JSON:
{{
  "blocked": true or false,
  "reasoning": "brief one sentence explanation"
}}
"""

    try:
        response = model.models.generate_content(
            model="gemini-2.5-flash",
            contents={"text": prompt},
            config={
                "temperature": 0,
                "top_p": 0.0,
                "top_k": 1,
            },
        )

        if hasattr(response, "text"):
            raw = response.text.strip()
        else:
            raw = ""
            output = getattr(response, "output", None)
            if output:
                first_output = output[0]
                content = getattr(first_output, "content", None)
                if content:
                    first_content = content[0]
                    raw = getattr(first_content, "text", "").strip()

        raw = raw.strip()

        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        return {
            "blocked": bool(result.get("blocked", False)),
            "reasoning": str(result.get("reasoning", "No reasoning provided")),
        }

    except json.JSONDecodeError as e:
        logger.error(f"LLM JSON parse error: {e} — raw: {response.text}")
        return {"blocked": False, "reasoning": "LLM response could not be parsed"}
    except Exception as e:
        logger.error(f"LLM analysis error: {e}")
        return {"blocked": False, "reasoning": "LLM analysis failed"}


# ── Public Service Functions ──────────────────────────────────────────────────

def check_domain(url: str, repo: DomainRepository) -> bool:
    """
    Fast check: is this domain blocked?

    Flow:
    1. Exact match in Firestore       → blocked (fastest)
    2. Vector similarity >= 0.85      → blocked + save to Firestore
    3. Otherwise                      → not blocked

    No scraping — this needs to be fast.
    Returns True if blocked, False if not.
    """
    domain = _normalize_url(url)

    # 1. Exact Firestore lookup
    if repo.exists(url):
        logger.info(f"Check '{domain}' → blocked (exact match)")
        return True

    # 2. Vector similarity
    similarity = _vector_search(domain)
    if similarity >= CHECK_SIMILARITY_THRESHOLD:
        reasoning = f"Domain name similarity {similarity:.2f} to known gambling domains"
        repo.save(url, reasoning)
        logger.info(f"Check '{domain}' → blocked (vector {similarity:.2f})")
        return True

    logger.info(f"Check '{domain}' → not blocked")
    return False


def report_domain(url: str, repo: DomainRepository) -> None:
    """
    Background task: analyze and potentially save a reported domain.

    Flow:
    1. Exact match in Firestore       → already known, skip
    2. Vector similarity >= 0.75      → save with similarity reasoning
    3. Scrape + LLM analysis          → save if LLM says blocked
    """
    domain = _normalize_url(url)

    # 1. Already in Firestore
    if repo.exists(url):
        logger.info(f"Report '{domain}' → already in Firestore, skipping")
        return

    # 2. Vector similarity
    similarity = _vector_search(domain)
    if similarity >= REPORT_SIMILARITY_THRESHOLD:
        reasoning = f"Domain name similarity {similarity:.2f} to known gambling domains"
        repo.save(url, reasoning)
        logger.info(f"Report '{domain}' → saved via vector similarity")
        return

    # 3. Scrape + LLM
    logger.info(f"Report '{domain}' → below threshold ({similarity:.2f}), scraping...")
    signals = scrape_domain_signals(url)

    if signals is None:
        logger.warning(f"Report '{domain}' → scrape failed, cannot analyze")
        return

    result = _llm_analyze(signals)

    if result["blocked"]:
        repo.save(url, result["reasoning"])
        logger.info(f"Report '{domain}' → saved via LLM: {result['reasoning']}")
    else:
        logger.info(f"Report '{domain}' → LLM says not gambling: {result['reasoning']}")