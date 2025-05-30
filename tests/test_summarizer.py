import importlib
from pathlib import Path

from oneforall.agents.summarizer import SummarizerAgent


def test_summarizer_offline(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path))
    import oneforall.db.vector_store as vs

    importlib.reload(vs)

    hits = [{"title": "x", "href": "https://example.com", "body": "demo"}]

    class FakeResp:
        text = "<p>Hello world article.</p>"

        @staticmethod
        def raise_for_status() -> None: ...

    monkeypatch.setattr("httpx.get", lambda *_a, **_kw: FakeResp())
    monkeypatch.setattr(
        "oneforall.agents.summarizer.chat",
        lambda *_a, **_kw: "- bullet A\n- bullet B",
    )

    out = SummarizerAgent().run(hits)
    assert out[0]["summary"].startswith("- bullet A")
