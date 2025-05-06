from __future__ import annotations

from typing import List

import httpx
from bs4 import BeautifulSoup
from oneforall.db.vector_store import store
from oneforall.llm.ollama_client import chat

SYSTEM_PROMPT = """
You are a professional research assistant.
Summarise the following web article in 3–4 concise bullet points.
Keep technical details (metrics, dates) and omit marketing fluff.
Return plain-text bullets (no JSON, no markdown).
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")  # built-in parser
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()
    return " ".join(soup.stripped_strings)


def _summarise(text: str, temperature: float = 0.2) -> str:
    return chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=temperature,
    )


class SummarizerAgent:
    """Download each hit, summarise it, then cache the summary."""

    def __init__(self, *, temperature: float = 0.2, max_chars: int = 4_000) -> None:
        self.temperature = temperature
        self.max_chars = max_chars

    def run(self, hits: List[dict]) -> List[dict]:
        results: List[dict] = []

        for hit in hits:
            url = hit["href"]

            # ----- cache check -------------------------------------------------
            cached = store.get(ids=[url], include=["documents"])
            if cached["documents"]:
                results.append({**hit, "summary": cached["documents"][0]})
                continue

            # ----- fetch & summarise ------------------------------------------
            try:
                resp = httpx.get(url, headers=HEADERS, timeout=30)
                resp.raise_for_status()
                text = _extract_text(resp.text)[: self.max_chars]
                summary = _summarise(text, self.temperature)
            except Exception as exc:
                summary = f"[Skipped] Could not fetch article ({exc.__class__.__name__})."

            # ----- persist -----------------------------------------------------
            store.add(ids=[url], documents=[summary], metadatas=[{"cached": True}])
            results.append({**hit, "summary": summary})

        return results
