from pathlib import Path

from oneforall.agents.citation import CitationAgent


def test_citation_offline(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path))

    html = """
    <meta name="citation_title" content="Edge LLMs Revolution">
    <meta name="citation_author" content="J. Doe">
    <meta name="citation_publication_date" content="2024-10-01">
    """

    class FakeResp:
        text = html

        @staticmethod
        def raise_for_status() -> None: ...

    monkeypatch.setattr("httpx.get", lambda *_a, **_kw: FakeResp())

    hit = {"title": "stub", "href": "https://example.com", "body": "x"}
    ref = CitationAgent().run([hit])[0]

    assert "J. Doe." in ref and "(2024)" in ref and "example.com" in ref
