def test_import() -> None:
    import importlib

    assert importlib.import_module("oneforall") is not None
