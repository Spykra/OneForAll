import importlib


def test_searcher_cache(tmp_path, monkeypatch):
    """First call hits stubbed DDG, second call is served from cache."""
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path))

    # reload modules so vector_store picks up new CHROMA_PATH
    import oneforall.db.vector_store as vs

    importlib.reload(vs)
    import oneforall.agents.searcher as searcher_mod

    importlib.reload(searcher_mod)

    # ----- stub DDGS to avoid real HTTP -----
    fake_hit = {"href": "https://example.com", "title": "stub", "body": "stub"}

    class FakeDDGS:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def text(self, *_, **__):
            return [fake_hit]

    monkeypatch.setattr(searcher_mod, "DDGS", FakeDDGS)

    # run twice and ensure second result is identical (cache)
    SearcherAgent = searcher_mod.SearcherAgent
    hits_first = SearcherAgent().run(["edge", "LLM", "2025"])
    assert hits_first == [fake_hit]

    hits_second = SearcherAgent().run(["edge", "LLM", "2025"])
    assert hits_second == hits_first
