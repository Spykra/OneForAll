import json
import re

from oneforall.agents.planner import PlannerAgent


def _stub_chat(*_, **__) -> str:
    """Offline stub for oneforall.agents.planner.chat."""
    return json.dumps(
        {
            "keywords": ["edge", "LLM", "2025"],
            "sections": ["Intro", "Use-cases"],
        }
    )


def test_plan_structure(monkeypatch):
    # prevent network traffic to Ollama
    monkeypatch.setattr("oneforall.agents.planner.chat", _stub_chat)

    plan = PlannerAgent().run("Edge LLMs 2025")

    assert list(plan) == ["keywords", "sections"]
    assert isinstance(plan["keywords"], list)
    assert isinstance(plan["sections"], list)
    assert all(re.fullmatch(r"[A-Za-z0-9\- ]{2,}", kw) for kw in plan["keywords"])
