import importlib

import pytest

from app.back_end.services.rust_bridge import get_rust_backend_version


class _MockRustModule:
    @staticmethod
    def backend_version() -> str:
        return "0.1.0"


class _MockBadRustModule:
    @staticmethod
    def backend_version() -> int:
        return 1


def test_get_rust_backend_version_returns_non_empty_string(monkeypatch):
    monkeypatch.setattr(importlib, "import_module", lambda _: _MockRustModule())
    assert get_rust_backend_version() == "0.1.0"


def test_get_rust_backend_version_raises_runtime_error_when_module_missing(monkeypatch):
    def _raise_module_not_found(_: str):
        raise ModuleNotFoundError("missing rust module")

    monkeypatch.setattr(importlib, "import_module", _raise_module_not_found)

    with pytest.raises(RuntimeError, match="Rust backend module"):
        get_rust_backend_version()


def test_get_rust_backend_version_raises_type_error_for_invalid_return_type(monkeypatch):
    monkeypatch.setattr(importlib, "import_module", lambda _: _MockBadRustModule())

    with pytest.raises(TypeError, match="must return a string"):
        get_rust_backend_version()
