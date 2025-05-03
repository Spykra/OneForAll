from __future__ import annotations

import json
from dataclasses import dataclass

from oneforall.llm.ollama_client import chat

SYSTEM_PROMPT = """
You are a research-planner agent. 
Given a topic, output STRICT JSON with keys:
  "keywords":  [str, ...]         # ≤8 search tokens
  "sections":  [str, ...]         # report outline
Return nothing else.
"""


@dataclass(slots=True)
class PlannerAgent:
    temperature: float = 0.0

    def run(self, topic: str) -> dict:
        user = f"Topic: {topic}"
        raw = chat(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}],
            temperature=self.temperature,
        )
        data = json.loads(raw)
        if not {"keywords", "sections"} <= data.keys():
            raise ValueError("PlannerAgent: missing required keys")
        return data
