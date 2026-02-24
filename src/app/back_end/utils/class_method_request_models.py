from pydantic import BaseModel, ConfigDict


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TrackPathRequest(BaseRequestModel):
    path: str


class PlaylistReorderRequest(BaseRequestModel):
    playlist_id: str
    ordered_track_ids: list[str]
