from pathlib import Path

from oneforall.agents.critic import CriticAgent
from oneforall.agents.writer import WriterAgent


def test_writer_and_critic(monkeypatch, tmp_path: Path) -> None:
    # stub chat to avoid LLM
    monkeypatch.setattr(
        "oneforall.agents.writer.chat",
        lambda *_, **__: "Body text.",  # returns deterministic body
    )

    outline = ["Intro", "Challenges"]
    summaries = [
        {"title": "Intro", "summary": "- A\n- B"},
        {"title": "Challenges", "summary": "- X\n- Y"},
    ]

    md = WriterAgent().run(outline, summaries)
    assert "## Intro" in md and "## Challenges" in md

    issues = CriticAgent().run(outline, md)
    assert issues == []  # should pass
