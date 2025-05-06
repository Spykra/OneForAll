from __future__ import annotations

import json
from typing import List

from duckduckgo_search import DDGS
from oneforall.db.vector_store import store


class SearcherAgent:
    """Fetches web hits for *keywords* and caches them in Chroma.

    Storage layout
    --------------
    • id ........  full query string
    • documents .. JSON-encoded list[dict]  ← the actual hits
    • metadatas .. {"cached": true}         ← scalar values only
    """

    def run(self, keywords: List[str], *, k: int = 6) -> List[dict]:
        query = " ".join(keywords).strip()

        # ---------- cache lookup ----------
        cached = store.get(ids=[query], include=["documents"])
        if cached["documents"]:
            return json.loads(cached["documents"][0])

        # ---------- live search ----------
        with DDGS() as ddgs:
            hits: List[dict] = list(ddgs.text(query, max_results=k))

        # ---------- write to cache ----------
        store.add(
            ids=[query],
            documents=[json.dumps(hits)],
            metadatas=[{"cached": True}],
        )
        return hits
