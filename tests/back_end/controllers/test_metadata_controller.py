from pathlib import Path

from app.back_end.utils.class_method_response_models import ErrorResponse, SuccessResponse
from app.back_end.controllers.metadata_controller import MetadataController
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class _InMemoryMetadataBridge:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, str]] = {}

    def read_metadata(self, path: str):
        current = self._store.get(path, {})
        data = {
            "path": path,
            "title": current.get("title", Path(path).stem),
            "artist": current.get("artist", ""),
            "album": current.get("album", ""),
            "genre": current.get("genre", ""),
        }
        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.METADATA_READ_COMPLETED,
            data=data,
        )

    def write_metadata(self, path: str, changes: dict[str, str]):
        current = self._store.setdefault(path, {})
        updated_fields: list[str] = []
        for key, value in changes.items():
            if value == "":
                current.pop(key, None)
            else:
                current[key] = value
            updated_fields.append(key)

        return SuccessResponse[dict[str, str | list[str]]](
            message=SuccessMessage.METADATA_WRITE_COMPLETED,
            data={"path": path, "updated_fields": sorted(updated_fields)},
        )


def test_metadata_update_persists_to_file(tmp_path):
    sample_audio_file = tmp_path / "sample.mp3"
    sample_audio_file.touch()

    bridge = _InMemoryMetadataBridge()
    controller = MetadataController(
        metadata_reader=bridge.read_metadata,
        metadata_writer=bridge.write_metadata,
    )

    response = controller.update_metadata(str(sample_audio_file), {"title": "New Title"})

    assert response.status is True
    assert response.message is SuccessMessage.METADATA_WRITE_COMPLETED

    refreshed = controller.read_metadata(str(sample_audio_file))
    assert refreshed.status is True
    assert refreshed.message is SuccessMessage.METADATA_READ_COMPLETED
    assert refreshed.data["title"] == "New Title"


def test_metadata_delete_clears_existing_value(tmp_path):
    sample_audio_file = tmp_path / "sample.mp3"
    sample_audio_file.touch()

    bridge = _InMemoryMetadataBridge()
    controller = MetadataController(
        metadata_reader=bridge.read_metadata,
        metadata_writer=bridge.write_metadata,
    )

    controller.update_metadata(str(sample_audio_file), {"album": "Album X"})
    response = controller.update_metadata(str(sample_audio_file), {"album": ""})

    assert response.status is True
    refreshed = controller.read_metadata(str(sample_audio_file))
    assert refreshed.data["album"] == ""


def test_update_metadata_returns_error_for_empty_changes(tmp_path):
    sample_audio_file = tmp_path / "sample.mp3"
    sample_audio_file.touch()

    bridge = _InMemoryMetadataBridge()
    controller = MetadataController(
        metadata_reader=bridge.read_metadata,
        metadata_writer=bridge.write_metadata,
    )

    response = controller.update_metadata(str(sample_audio_file), {})

    assert response.status is False
    assert response.message is ErrorMessage.INVALID_METADATA_CHANGES
    assert response.data is None


def test_update_metadata_propagates_bridge_failure(tmp_path):
    sample_audio_file = tmp_path / "sample.mp3"
    sample_audio_file.touch()

    bridge = _InMemoryMetadataBridge()

    def _failing_writer(path: str, changes: dict[str, str]):
        return ErrorResponse(message=ErrorMessage.RUST_BACKEND_OPERATION_FAILED)

    controller = MetadataController(
        metadata_reader=bridge.read_metadata,
        metadata_writer=_failing_writer,
    )

    response = controller.update_metadata(str(sample_audio_file), {"title": "New"})

    assert response.status is False
    assert response.message is ErrorMessage.RUST_BACKEND_OPERATION_FAILED
    assert response.data is None
