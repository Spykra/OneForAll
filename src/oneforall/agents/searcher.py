from __future__ import annotations

import json
from typing import List
from urllib.parse import urlparse

from duckduckgo_search import DDGS
from oneforall.db.vector_store import store


def _score(hit: dict) -> int:
    """0 = scholarly/official • 1 = neutral • 2 = low-signal."""
    domain = urlparse(hit["href"]).netloc.lower()
    if any(d in domain for d in ("arxiv.org", "acm.org", ".gov", ".edu", "ieee.org", "nature.com")):
        return 0
    if any(d in domain for d in ("youtube.com", "youtu.be", "medium.com", "blogspot", "wordpress")):
        return 2
    return 1


class SearcherAgent:
    """DuckDuckGo → Chroma-cached search."""

    def run(self, keywords: List[str], *, k: int = 6) -> List[dict]:
        query = " ".join(keywords).strip().lower()

        cached = store.get(ids=[query], include=["documents"])
        if cached["documents"]:
            return json.loads(cached["documents"][0])

        with DDGS() as ddgs:
            hits: List[dict] = list(ddgs.text(query, max_results=k))

        hits.sort(key=_score)
        store.add(ids=[query], documents=[json.dumps(hits)], metadatas=[{"cached": True}])
        return hits
