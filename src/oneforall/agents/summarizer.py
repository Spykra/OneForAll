from __future__ import annotations

import logging
from typing import List

import httpx
from bs4 import BeautifulSoup
from oneforall.db.vector_store import store
from oneforall.llm.ollama_client import chat
from oneforall.utils.http import HEADERS

log = logging.getLogger(__name__)

_SYS = "You are a research assistant. List the article’s main points in 3-4 bullet lines starting with •."


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()
    return " ".join(soup.stripped_strings)


def _summarise(text: str, temperature: float) -> str:
    return chat([{"role": "system", "content": _SYS}, {"role": "user", "content": text}], temperature=temperature)


class SummarizerAgent:
    """Download, summarise, and cache articles."""

    def __init__(self, *, temperature: float = 0.2, max_chars: int = 8_000) -> None:
        self.temperature = temperature
        self.max_chars = max_chars

    def run(self, hits: List[dict]) -> List[dict]:
        out: List[dict] = []
        for hit in hits:
            url = hit["href"]

            cached = store.get(ids=[url], include=["documents"])
            if cached["documents"]:
                out.append({**hit, "summary": cached["documents"][0]})
                continue

            try:
                r = httpx.get(url, headers=HEADERS, timeout=30)
                r.raise_for_status()
            except httpx.HTTPStatusError:
                alt = f"https://r.jina.ai/http://{url.lstrip('https://')}"
                try:
                    r = httpx.get(alt, timeout=15)
                except httpx.HTTPError as exc:
                    summary = f"[Skipped] Could not fetch article ({exc.__class__.__name__})."
                    store.add(ids=[url], documents=[summary], metadatas=[{"cached": True}])
                    out.append({**hit, "summary": summary})
                    continue
            except Exception as exc:
                summary = f"[Skipped] Could not fetch article ({exc.__class__.__name__})."
                store.add(ids=[url], documents=[summary], metadatas=[{"cached": True}])
                out.append({**hit, "summary": summary})
                continue

            text = _extract_text(r.text)[: self.max_chars]
            if len(text.split()) < 150:
                summary = "[Skipped] Article too short."
            else:
                summary = _summarise(text, self.temperature)

            store.add(ids=[url], documents=[summary], metadatas=[{"cached": True}])
            out.append({**hit, "summary": summary})
        return out
