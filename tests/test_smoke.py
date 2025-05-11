import importlib


def test_import() -> None:
    assert importlib.import_module("oneforall") is not None
