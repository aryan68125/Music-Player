from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, field_validator


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TrackPathRequest(BaseRequestModel):
    path: str

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Path cannot be empty.")
        return value


class PlaylistReorderRequest(BaseRequestModel):
    playlist_id: str
    ordered_track_ids: list[str]


class LibraryScanRequest(BaseRequestModel):
    paths: list[str]

    @field_validator("paths")
    @classmethod
    def validate_paths(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("At least one scan path is required.")
        for path in value:
            if not path.strip():
                raise ValueError("Scan paths cannot include empty values.")
        return value


MetadataValue: TypeAlias = str | int | float | bool


class MetadataWriteRequest(BaseRequestModel):
    path: str
    changes: dict[str, MetadataValue]

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Path cannot be empty.")
        return value

    @field_validator("changes")
    @classmethod
    def validate_changes(cls, value: dict[str, MetadataValue]) -> dict[str, MetadataValue]:
        if not value:
            raise ValueError("Metadata changes cannot be empty.")
        return value


class ArtworkReplaceRequest(BaseRequestModel):
    track_path: str
    image_path: str

    @field_validator("track_path", "image_path")
    @classmethod
    def validate_non_empty_path(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Path cannot be empty.")
        return value
