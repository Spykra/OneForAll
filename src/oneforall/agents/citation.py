from __future__ import annotations

import logging
import re
from typing import List

import httpx
from bs4 import BeautifulSoup
from oneforall.utils.http import HEADERS

log = logging.getLogger(__name__)


def _extract_meta(html: str, *names: str) -> str | None:
    """Return first non-empty meta[name|property] content."""
    soup = BeautifulSoup(html, "html.parser")
    for name in names:
        tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def _year(date: str | None) -> str | None:
    if not date:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", date)
    return m.group(0) if m else None


class CitationAgent:
    """Build short APA-like citations from *hits*."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def _cite(self, hit: dict) -> str:
        url = hit["href"]
        html = ""
        try:
            r = httpx.get(url, headers=HEADERS, timeout=self.timeout)
            r.raise_for_status()
            html = r.text
        except Exception as exc:  # noqa: BLE001
            log.debug("Citation fetch failed for %s – %s", url, exc.__class__.__name__)

        title = _extract_meta(html, "citation_title", "og:title") or hit["title"].rstrip(" .")
        author = _extract_meta(html, "citation_author", "author", "article:author")
        year = _year(
            _extract_meta(
                html,
                "citation_publication_date",
                "citation_date",
                "article:published_time",
                "og:updated_time",
            )
        )

        parts = [
            f"{author}." if author else "",
            f"*{title}*." if title else "",
            f"({year})." if year else "",
            f"{url}.",
        ]
        return " ".join(p for p in parts if p)

    def run(self, hits: List[dict]) -> List[str]:
        return sorted({self._cite(h) for h in hits if h})
