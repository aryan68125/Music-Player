from __future__ import annotations

from collections.abc import Callable

from pydantic import ValidationError

from app.back_end.services import rust_bridge
from app.back_end.utils.class_method_request_models import MetadataValue, MetadataWriteRequest, TrackPathRequest
from app.back_end.utils.class_method_response_models import ErrorResponse, MethodResponse
from app.back_end.utils.error_messages import ErrorMessage

MetadataReader = Callable[[str], MethodResponse[dict[str, str]]]
MetadataWriter = Callable[[str, dict[str, MetadataValue]], MethodResponse[dict[str, str | list[str]]]]


class MetadataController:
    def __init__(
        self,
        metadata_reader: MetadataReader | None = None,
        metadata_writer: MetadataWriter | None = None,
    ) -> None:
        self._metadata_reader = metadata_reader or rust_bridge.read_metadata
        self._metadata_writer = metadata_writer or rust_bridge.write_metadata

    def read_metadata(self, path: str) -> MethodResponse[dict[str, str]]:
        try:
            request = TrackPathRequest(path=path)
        except ValidationError:
            return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND)

        return self._metadata_reader(request.path)

    def update_metadata(
        self,
        path: str,
        changes: dict[str, MetadataValue],
    ) -> MethodResponse[dict[str, str | list[str]]]:
        normalized_changes = self._normalize_changes(changes)

        try:
            request = MetadataWriteRequest(path=path, changes=normalized_changes)
        except ValidationError:
            return ErrorResponse(message=ErrorMessage.INVALID_METADATA_CHANGES)

        return self._metadata_writer(request.path, request.changes)

    @staticmethod
    def _normalize_changes(changes: dict[str, MetadataValue]) -> dict[str, MetadataValue]:
        normalized: dict[str, MetadataValue] = {}
        for key, value in changes.items():
            cleaned_key = str(key).strip()
            if not cleaned_key:
                continue
            if isinstance(value, str):
                normalized[cleaned_key] = value.strip()
            else:
                normalized[cleaned_key] = value
        return normalized
