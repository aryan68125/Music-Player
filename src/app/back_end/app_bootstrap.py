from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.back_end.controllers.favorites_controller import FavoritesController
from app.back_end.controllers.metadata_controller import MetadataController
from app.back_end.controllers.playlist_controller import PlaylistController
from app.back_end.data.database_handler.database import DatabaseHandler
from app.back_end.data.repositories.repository import Repository
from app.back_end.services.playback_service import PlaybackBackendProtocol, PlaybackService
from app.back_end.services.queue_service import QueueService


@dataclass(slots=True)
class AppBootstrap:
    db_handler: DatabaseHandler
    repository: Repository
    playback: PlaybackService
    playlists: PlaylistController
    favorites: FavoritesController
    metadata: MetadataController

    @classmethod
    def create(
        cls,
        db_path: str | Path,
        playback_backend: PlaybackBackendProtocol,
    ) -> AppBootstrap:
        db_handler = DatabaseHandler(db_path=db_path)
        db_handler.initialize_schema()

        repository = Repository(db_handler)
        return cls(
            db_handler=db_handler,
            repository=repository,
            playback=PlaybackService(playback_backend),
            playlists=PlaylistController(repository),
            favorites=FavoritesController(repository),
            metadata=MetadataController(),
        )

    def register_track(
        self,
        path: str,
        title: str = "",
        artist: str = "",
        album: str = "",
        duration_ms: int = 0,
    ) -> int:
        self.repository.execute(
            "INSERT INTO tracks (path, title, artist, album, duration_ms) VALUES (?, ?, ?, ?, ?)",
            (path, title, artist, album, duration_ms),
        )
        row = self.repository.fetch_one("SELECT id FROM tracks WHERE path = ? LIMIT 1", (path,))
        if row is None:
            raise RuntimeError("Track insert failed.")
        return int(row[0])

    def build_queue_for_playlist(self, playlist_id: int) -> QueueService:
        ordered_track_ids = self.playlists.get_playlist_track_ids(playlist_id)
        return QueueService(track_ids=[str(track_id) for track_id in ordered_track_ids])

    def close(self) -> None:
        self.db_handler.close()
