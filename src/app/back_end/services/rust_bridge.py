import importlib
from types import ModuleType

from pydantic import ValidationError

from app.back_end.utils.class_method_request_models import LibraryScanRequest, MetadataWriteRequest, TrackPathRequest
from app.back_end.utils.class_method_response_models import ErrorResponse, MethodResponse, SuccessResponse
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


def _load_rust_backend_module() -> ModuleType:
    try:
        return importlib.import_module("rust_back_end_native")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Rust backend module 'rust_back_end_native' is not installed. "
            "Build it with 'venv/bin/python -m maturin develop --manifest-path rust_back_end/Cargo.toml'."
        ) from exc


def get_rust_backend_version() -> str:
    module = _load_rust_backend_module()

    if not hasattr(module, "backend_version"):
        raise RuntimeError("Rust backend module is missing required function 'backend_version'.")

    version = module.backend_version()
    if not isinstance(version, str):
        raise TypeError("Rust backend function 'backend_version' must return a string.")
    if not version.strip():
        raise ValueError("Rust backend version must be a non-empty string.")

    return version


def scan_library(paths: list[str]) -> MethodResponse[dict[str, str]]:
    try:
        request = LibraryScanRequest(paths=paths)
    except ValidationError:
        return ErrorResponse(message=ErrorMessage.INVALID_LIBRARY_SCAN_PATHS)

    try:
        module = _load_rust_backend_module()
        raw_paths = module.scan_library(request.paths)
        normalized = [{"path": str(path)} for path in raw_paths if str(path).strip()]
        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.LIBRARY_SCAN_COMPLETED,
            data=normalized,
        )
    except Exception:
        return ErrorResponse(message=ErrorMessage.RUST_BACKEND_OPERATION_FAILED)


def read_metadata(path: str) -> MethodResponse[dict[str, str]]:
    try:
        request = TrackPathRequest(path=path)
    except ValidationError:
        return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND)

    try:
        module = _load_rust_backend_module()
        raw_metadata = module.read_metadata(request.path)
        normalized = {str(key): str(value) for key, value in dict(raw_metadata).items()}
        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.METADATA_READ_COMPLETED,
            data=normalized,
        )
    except Exception:
        return ErrorResponse(message=ErrorMessage.RUST_BACKEND_OPERATION_FAILED)


def write_metadata(path: str, changes: dict[str, str | int | float | bool]) -> MethodResponse[dict[str, str | list[str]]]:
    try:
        request = MetadataWriteRequest(path=path, changes=changes)
    except ValidationError:
        return ErrorResponse(message=ErrorMessage.INVALID_METADATA_CHANGES)

    try:
        module = _load_rust_backend_module()
        normalized_changes = {key: str(value) for key, value in request.changes.items()}
        updated_fields = [str(field) for field in module.write_metadata(request.path, normalized_changes)]
        return SuccessResponse[dict[str, str | list[str]]](
            message=SuccessMessage.METADATA_WRITE_COMPLETED,
            data={"path": request.path, "updated_fields": updated_fields},
        )
    except Exception:
        return ErrorResponse(message=ErrorMessage.RUST_BACKEND_OPERATION_FAILED)


def extract_artwork(path: str) -> MethodResponse[dict[str, bytes | None]]:
    try:
        request = TrackPathRequest(path=path)
    except ValidationError:
        return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND)

    try:
        module = _load_rust_backend_module()
        artwork_bytes = module.extract_artwork(request.path)
        if artwork_bytes is not None and not isinstance(artwork_bytes, bytes):
            artwork_bytes = bytes(artwork_bytes)
        return SuccessResponse[dict[str, bytes | None]](
            message=SuccessMessage.ARTWORK_EXTRACTION_COMPLETED,
            data={"artwork_bytes": artwork_bytes},
        )
    except Exception:
        return ErrorResponse(message=ErrorMessage.RUST_BACKEND_OPERATION_FAILED)
