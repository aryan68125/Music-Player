from pathlib import Path

from app.back_end.services.artwork_service import ArtworkService
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


def _write_jpeg(path: Path) -> None:
    # Minimal JPEG-like bytes with SOI marker.
    path.write_bytes(b"\xFF\xD8\xFF\xE0" + b"jpeg-data")


def _write_png(path: Path) -> None:
    # PNG signature plus filler bytes.
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"png-data")


def test_replace_artwork_dispatches_to_mp3_handler(monkeypatch, tmp_path):
    track = tmp_path / "track.mp3"
    track.touch()
    image = tmp_path / "cover.jpg"
    _write_jpeg(image)

    called: dict[str, object] = {}
    service = ArtworkService()

    def _fake_replace_mp3(track_path: Path, image_data: bytes, mime: str) -> None:
        called["track"] = track_path
        called["mime"] = mime
        called["size"] = len(image_data)

    monkeypatch.setattr(service, "_replace_mp3", _fake_replace_mp3)

    response = service.replace_artwork(str(track), str(image))

    assert response.status is True
    assert response.message is SuccessMessage.ARTWORK_UPDATED
    assert called["track"] == track
    assert called["mime"] == "image/jpeg"
    assert int(called["size"]) > 0


def test_replace_artwork_returns_error_for_unsupported_audio_format(tmp_path):
    track = tmp_path / "track.ogg"
    track.touch()
    image = tmp_path / "cover.jpg"
    _write_jpeg(image)

    service = ArtworkService()
    response = service.replace_artwork(str(track), str(image))

    assert response.status is False
    assert response.message is ErrorMessage.ARTWORK_FORMAT_NOT_SUPPORTED
    assert response.data is None


def test_replace_artwork_returns_error_for_missing_image(tmp_path):
    track = tmp_path / "track.mp3"
    track.touch()

    service = ArtworkService()
    response = service.replace_artwork(str(track), str(tmp_path / "missing.jpg"))

    assert response.status is False
    assert response.message is ErrorMessage.ARTWORK_IMAGE_NOT_FOUND
    assert response.data is None


def test_replace_artwork_returns_error_for_invalid_image_bytes(tmp_path):
    track = tmp_path / "track.mp3"
    track.touch()
    image = tmp_path / "cover.jpg"
    image.write_bytes(b"not-an-image")

    service = ArtworkService()
    response = service.replace_artwork(str(track), str(image))

    assert response.status is False
    assert response.message is ErrorMessage.INVALID_ARTWORK_IMAGE
    assert response.data is None


def test_replace_artwork_returns_error_when_handler_raises(monkeypatch, tmp_path):
    track = tmp_path / "track.mp3"
    track.touch()
    image = tmp_path / "cover.png"
    _write_png(image)

    service = ArtworkService()

    def _failing_replace_mp3(*_args, **_kwargs) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(service, "_replace_mp3", _failing_replace_mp3)

    response = service.replace_artwork(str(track), str(image))

    assert response.status is False
    assert response.message is ErrorMessage.ARTWORK_UPDATE_FAILED
    assert response.data is None


def test_remove_artwork_dispatches_to_flac_handler(monkeypatch, tmp_path):
    track = tmp_path / "track.flac"
    track.touch()

    called: dict[str, Path] = {}
    service = ArtworkService()

    def _fake_remove_flac(track_path: Path) -> None:
        called["track"] = track_path

    monkeypatch.setattr(service, "_remove_flac", _fake_remove_flac)

    response = service.remove_artwork(str(track))

    assert response.status is True
    assert response.message is SuccessMessage.ARTWORK_REMOVED
    assert called["track"] == track


def test_remove_artwork_returns_error_for_unsupported_audio_format(tmp_path):
    track = tmp_path / "track.wav"
    track.touch()

    service = ArtworkService()
    response = service.remove_artwork(str(track))

    assert response.status is False
    assert response.message is ErrorMessage.ARTWORK_FORMAT_NOT_SUPPORTED
    assert response.data is None


def test_remove_artwork_returns_error_when_handler_raises(monkeypatch, tmp_path):
    track = tmp_path / "track.m4a"
    track.touch()

    service = ArtworkService()

    def _failing_remove_mp4(*_args, **_kwargs) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(service, "_remove_mp4", _failing_remove_mp4)

    response = service.remove_artwork(str(track))

    assert response.status is False
    assert response.message is ErrorMessage.ARTWORK_REMOVE_FAILED
    assert response.data is None
