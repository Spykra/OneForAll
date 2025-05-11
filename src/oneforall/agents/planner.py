from __future__ import annotations

import ast
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict

from oneforall.llm.ollama_client import chat

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a research-planner agent.

Given a topic, output JSON:
{
  "keywords":  [str, ...],   # ≤8 tokens, no quotes/punctuation
  "sections":  [str, ...]    # 2–4-word headings
}

Exclude generic buzzwords (“AI”, “Machine Learning”, …) unless essential.
Return *only* JSON (no markdown, code fences, or commentary).
""".strip()


@dataclass(slots=True)
class PlannerAgent:
    temperature: float = 0.0
    max_retries: int = 3

    @staticmethod
    def _strip_wrappers(text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.lstrip("`").lstrip("json").strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
        return cleaned

    @staticmethod
    def _first_json(text: str) -> str | None:
        for m in re.finditer(r"\{.*?\}", text, flags=re.S):
            snippet = m.group(0)
            try:
                json.loads(snippet)
                return snippet
            except json.JSONDecodeError:
                continue
        return None

    def run(self, topic: str) -> Dict[str, Any]:
        """Return {"keywords": [...], "sections": [...]}."""
        user_msg = f"Topic: {topic}"
        last_err: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            raw = chat(
                [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_msg}],
                temperature=self.temperature,
            )

            for candidate in (
                raw,
                self._strip_wrappers(raw),
                self._first_json(raw),
                self._strip_wrappers(self._first_json(raw) or ""),
            ):
                if not candidate:
                    continue
                try:
                    data = json.loads(candidate)
                    break
                except (json.JSONDecodeError, SyntaxError):
                    try:
                        data = ast.literal_eval(candidate)
                        if isinstance(data, dict):
                            break
                    except Exception as err:  # noqa: BLE001
                        last_err = err
            else:
                log.warning("Planner retry %d/%d – parse failure", attempt, self.max_retries)
                continue
            break  # success
        else:
            raise ValueError(f"PlannerAgent: could not parse LLM output – {last_err}") from last_err

        if not {"keywords", "sections"} <= data.keys():
            raise ValueError("PlannerAgent: missing required keys")

        data["keywords"] = [" ".join(t.split()[:3]) for t in data["keywords"]][:8]
        data["sections"] = [s.title().strip() for s in data["sections"][:8]]
        return data
