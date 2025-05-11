import importlib


def test_searcher_cache(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path))

    # reload to pick new CHROMA_PATH
    import oneforall.db.vector_store as vs

    importlib.reload(vs)
    import oneforall.agents.searcher as sm

    importlib.reload(sm)

    fake_hit = {"href": "https://example.com", "title": "stub", "body": "stub"}

    class FakeDDGS:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def text(self, *_a, **_kw):
            return [fake_hit]

    monkeypatch.setattr(sm, "DDGS", FakeDDGS)

    searcher = sm.SearcherAgent()
    first = searcher.run(["edge", "LLM", "2025"])
    second = searcher.run(["edge", "LLM", "2025"])

    assert first == [fake_hit] and second == first
