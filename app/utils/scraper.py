import httpx
from selectolax.lexbor import LexborHTMLParser
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

TIMEOUT = 10  # seconds


def _extract_text(node) -> str:
    """Safely extract and clean text from a node."""
    if node is None:
        return ""
    return " ".join(node.text(strip=True).split())


def scrape_domain_signals(url: str) -> dict | None:
    """
    Scrapes a domain and extracts signals to help determine if it's a gambling site.

    Targets:
    - <title>            — often the clearest signal ("Slot Online Terpercaya")
    - <meta description> — SEO description, usually reveals site purpose
    - <h1>, <h2>         — main page headings
    - <nav> / <header>   — navigation links (Slot, Togel, Daftar, Deposit)
    - <footer>           — license info, operator name, often most explicit
    - <button> text      — CTAs like "Daftar Sekarang", "Deposit"

    Returns None if the site is unreachable.
    """
    if not url.startswith("http"):
        url = f"https://{url}"

    try:
        response = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.warning(f"Scrape timeout: {url}")
        return None
    except httpx.HTTPError as e:
        logger.warning(f"Scrape HTTP error {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Scrape failed {url}: {e}")
        return None

    try:
        tree = LexborHTMLParser(response.text)

        title = _extract_text(tree.css_first("title"))

        meta_desc = ""
        meta_node = tree.css_first('meta[name="description"]')
        if meta_node:
            meta_desc = meta_node.attributes.get("content", "")

        headings = " | ".join(
            _extract_text(node)
            for node in tree.css("h1, h2")
            if _extract_text(node)
        )

        nav_links = " | ".join(
            _extract_text(node)
            for node in tree.css("nav a, header a")
            if _extract_text(node)
        )

        footer = _extract_text(tree.css_first("footer"))

        buttons = " | ".join(
            _extract_text(node)
            for node in tree.css("button, a.btn, a.button")
            if _extract_text(node)
        )

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "headings": headings[:500],     # cap length for LLM prompt
            "navigation": nav_links[:500],
            "footer": footer[:1000],        # footer is most important, give it more room
            "buttons": buttons[:300],
        }

    except Exception as e:
        logger.error(f"Parse error {url}: {e}")
        return None