from pathlib import Path

from oneforall.agents.critic import CriticAgent
from oneforall.agents.writer import WriterAgent


def test_writer_and_critic(monkeypatch, tmp_path: Path) -> None:
    """Writer should assemble markdown correctly and Critic should pass it."""
    monkeypatch.setattr("oneforall.agents.writer.chat", lambda *_a, **__: "Body text.")

    outline = ["Intro", "Challenges"]
    summaries = [
        {"title": "Intro", "summary": "- A\n- B"},
        {"title": "Challenges", "summary": "- X\n- Y"},
    ]

    md = WriterAgent().run(outline, summaries)

    assert all(md.count(f"## {section}") == 1 for section in outline)

    assert "####" not in md
    assert "---" not in md
    assert "====" not in md

    assert CriticAgent().run(outline, md) == []
