import os
from typing import Any, Dict, List

import httpx

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def chat(messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
    payload: Dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
        "options": {"temperature": temperature},
        "stream": False,
    }
    r = httpx.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]
