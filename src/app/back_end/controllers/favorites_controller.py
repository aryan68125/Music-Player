from app.back_end.data.repositories.repository import Repository
from app.back_end.utils.class_method_response_models import ErrorResponse, MethodResponse, SuccessResponse
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class FavoritesController:
    FAVORITES_PLAYLIST_NAME = "Favorites"
    FAVORITES_PLAYLIST_KIND = "smart"

    def __init__(self, repository: Repository) -> None:
        self._repository = repository
        self._ensure_favorites_playlist()

    def mark_favorite(self, track_id: int) -> MethodResponse[dict[str, int]]:
        if not self._track_exists(track_id):
            return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND)

        self._repository.execute(
            "UPDATE tracks SET is_favorite = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (track_id,),
        )

        playlist_id = self._ensure_favorites_playlist()
        if not self.is_in_favorites(track_id):
            position = self._next_position(playlist_id)
            self._repository.execute(
                "INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (?, ?, ?)",
                (playlist_id, track_id, position),
            )

        return SuccessResponse[dict[str, int]](
            message=SuccessMessage.TRACK_ADDED_TO_FAVORITES,
            data={"track_id": track_id},
        )

    def is_in_favorites(self, track_id: int) -> bool:
        playlist_id = self._get_favorites_playlist_id()
        if playlist_id is None:
            return False
        row = self._repository.fetch_one(
            "SELECT 1 FROM playlist_tracks WHERE playlist_id = ? AND track_id = ? LIMIT 1",
            (playlist_id, track_id),
        )
        return row is not None

    def _track_exists(self, track_id: int) -> bool:
        row = self._repository.fetch_one("SELECT 1 FROM tracks WHERE id = ? LIMIT 1", (track_id,))
        return row is not None

    def _get_favorites_playlist_id(self) -> int | None:
        row = self._repository.fetch_one(
            "SELECT id FROM playlists WHERE name = ? AND kind = ?",
            (self.FAVORITES_PLAYLIST_NAME, self.FAVORITES_PLAYLIST_KIND),
        )
        if row is None:
            return None
        return int(row[0])

    def _ensure_favorites_playlist(self) -> int:
        playlist_id = self._get_favorites_playlist_id()
        if playlist_id is not None:
            return playlist_id

        self._repository.execute(
            "INSERT INTO playlists (name, kind) VALUES (?, ?)",
            (self.FAVORITES_PLAYLIST_NAME, self.FAVORITES_PLAYLIST_KIND),
        )
        # Row exists immediately after insert.
        return int(self._get_favorites_playlist_id())

    def _next_position(self, playlist_id: int) -> int:
        row = self._repository.fetch_one(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM playlist_tracks WHERE playlist_id = ?",
            (playlist_id,),
        )
        return int(row[0]) if row is not None else 0
