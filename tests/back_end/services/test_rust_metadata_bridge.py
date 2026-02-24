import pytest

from app.back_end.services import rust_bridge
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class _FakeRustModule:
    @staticmethod
    def scan_library(paths: list[str]) -> list[str]:
        assert paths == ["/music"]
        return ["/music/a.mp3", "/music/b.flac"]

    @staticmethod
    def read_metadata(path: str) -> dict[str, str]:
        assert path == "/music/a.mp3"
        return {
            "path": path,
            "title": "Song A",
            "artist": "Artist A",
            "album": "Album A",
            "duration_ms": "120000",
        }

    @staticmethod
    def write_metadata(path: str, changes: dict[str, str]) -> list[str]:
        assert path == "/music/a.mp3"
        assert changes["title"] == "Updated"
        assert changes["track_number"] == "2"
        return sorted(changes.keys())

    @staticmethod
    def extract_artwork(path: str) -> bytes:
        assert path == "/music/a.mp3"
        return b"artwork-bytes"


class _BrokenRustModule:
    @staticmethod
    def scan_library(paths: list[str]) -> list[str]:
        raise RuntimeError("rust failure")



def test_scan_library_returns_success_response(monkeypatch):
    monkeypatch.setattr(rust_bridge, "_load_rust_backend_module", lambda: _FakeRustModule())

    response = rust_bridge.scan_library(["/music"])

    assert response.status is True
    assert response.message is SuccessMessage.LIBRARY_SCAN_COMPLETED
    assert response.data == [{"path": "/music/a.mp3"}, {"path": "/music/b.flac"}]



def test_scan_library_returns_error_for_invalid_paths_payload():
    response = rust_bridge.scan_library([])

    assert response.status is False
    assert response.message is ErrorMessage.INVALID_LIBRARY_SCAN_PATHS
    assert response.data is None



def test_read_metadata_returns_success_response(monkeypatch):
    monkeypatch.setattr(rust_bridge, "_load_rust_backend_module", lambda: _FakeRustModule())

    response = rust_bridge.read_metadata("/music/a.mp3")

    assert response.status is True
    assert response.message is SuccessMessage.METADATA_READ_COMPLETED
    assert response.data["title"] == "Song A"



def test_write_metadata_returns_success_response(monkeypatch):
    monkeypatch.setattr(rust_bridge, "_load_rust_backend_module", lambda: _FakeRustModule())

    response = rust_bridge.write_metadata("/music/a.mp3", {"title": "Updated", "track_number": 2})

    assert response.status is True
    assert response.message is SuccessMessage.METADATA_WRITE_COMPLETED
    assert response.data["path"] == "/music/a.mp3"
    assert response.data["updated_fields"] == ["title", "track_number"]



def test_extract_artwork_returns_success_response(monkeypatch):
    monkeypatch.setattr(rust_bridge, "_load_rust_backend_module", lambda: _FakeRustModule())

    response = rust_bridge.extract_artwork("/music/a.mp3")

    assert response.status is True
    assert response.message is SuccessMessage.ARTWORK_EXTRACTION_COMPLETED
    assert response.data == {"artwork_bytes": b"artwork-bytes"}



def test_scan_library_returns_operation_error_when_rust_raises(monkeypatch):
    monkeypatch.setattr(rust_bridge, "_load_rust_backend_module", lambda: _BrokenRustModule())

    response = rust_bridge.scan_library(["/music"])

    assert response.status is False
    assert response.message is ErrorMessage.RUST_BACKEND_OPERATION_FAILED
    assert response.data is None
