from app.back_end.data.repositories.repository import Repository
from app.back_end.utils.class_method_response_models import ErrorResponse, MethodResponse, SuccessResponse
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class PlaylistController:
    USER_PLAYLIST_KIND = "user"

    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def create_playlist(self, name: str) -> MethodResponse[dict[str, int | str]]:
        if not isinstance(name, str) or not name.strip():
            return ErrorResponse(message=ErrorMessage.INVALID_PLAYLIST_NAME)

        self._repository.execute(
            "INSERT INTO playlists (name, kind) VALUES (?, ?)",
            (name.strip(), self.USER_PLAYLIST_KIND),
        )
        row = self._repository.fetch_one(
            "SELECT id FROM playlists WHERE name = ? AND kind = ?",
            (name.strip(), self.USER_PLAYLIST_KIND),
        )
        playlist_id = int(row[0])

        return SuccessResponse[dict[str, int | str]](
            message=SuccessMessage.PLAYLIST_CREATED,
            data={"playlist_id": playlist_id, "name": name.strip()},
        )

    def rename_playlist(self, playlist_id: int, new_name: str) -> MethodResponse[dict[str, int | str]]:
        if not self._playlist_exists(playlist_id):
            return ErrorResponse(message=ErrorMessage.PLAYLIST_NOT_FOUND)
        if not isinstance(new_name, str) or not new_name.strip():
            return ErrorResponse(message=ErrorMessage.INVALID_PLAYLIST_NAME)

        self._repository.execute(
            "UPDATE playlists SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_name.strip(), playlist_id),
        )
        return SuccessResponse[dict[str, int | str]](
            message=SuccessMessage.PLAYLIST_UPDATED,
            data={"playlist_id": playlist_id, "name": new_name.strip()},
        )

    def delete_playlist(self, playlist_id: int) -> MethodResponse[dict[str, int]]:
        if not self._playlist_exists(playlist_id):
            return ErrorResponse(message=ErrorMessage.PLAYLIST_NOT_FOUND)

        self._repository.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
        return SuccessResponse[dict[str, int]](
            message=SuccessMessage.PLAYLIST_DELETED,
            data={"playlist_id": playlist_id},
        )

    def add_track_to_playlist(self, playlist_id: int, track_id: int) -> MethodResponse[dict[str, int]]:
        if not self._playlist_exists(playlist_id):
            return ErrorResponse(message=ErrorMessage.PLAYLIST_NOT_FOUND)
        if not self._track_exists(track_id):
            return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND)

        existing = self._repository.fetch_one(
            "SELECT 1 FROM playlist_tracks WHERE playlist_id = ? AND track_id = ? LIMIT 1",
            (playlist_id, track_id),
        )
        if existing is not None:
            return ErrorResponse(message=ErrorMessage.TRACK_ALREADY_IN_PLAYLIST)

        position = self._next_position(playlist_id)
        self._repository.execute(
            "INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (?, ?, ?)",
            (playlist_id, track_id, position),
        )

        return SuccessResponse[dict[str, int]](
            message=SuccessMessage.PLAYLIST_TRACKS_UPDATED,
            data={"playlist_id": playlist_id, "track_id": track_id},
        )

    def remove_track_from_playlist(self, playlist_id: int, track_id: int) -> MethodResponse[dict[str, int]]:
        if not self._playlist_exists(playlist_id):
            return ErrorResponse(message=ErrorMessage.PLAYLIST_NOT_FOUND)

        existing = self._repository.fetch_one(
            "SELECT 1 FROM playlist_tracks WHERE playlist_id = ? AND track_id = ? LIMIT 1",
            (playlist_id, track_id),
        )
        if existing is None:
            return ErrorResponse(message=ErrorMessage.TRACK_NOT_IN_PLAYLIST)

        self._repository.execute(
            "DELETE FROM playlist_tracks WHERE playlist_id = ? AND track_id = ?",
            (playlist_id, track_id),
        )
        self._normalize_positions(playlist_id)

        return SuccessResponse[dict[str, int]](
            message=SuccessMessage.PLAYLIST_TRACKS_UPDATED,
            data={"playlist_id": playlist_id, "track_id": track_id},
        )

    def reorder_tracks(self, playlist_id: int, ordered_track_ids: list[int]) -> MethodResponse[dict[str, int]]:
        if not self._playlist_exists(playlist_id):
            return ErrorResponse(message=ErrorMessage.PLAYLIST_NOT_FOUND)

        current_ids = self.get_playlist_track_ids(playlist_id)
        if sorted(current_ids) != sorted(ordered_track_ids) or len(current_ids) != len(ordered_track_ids):
            return ErrorResponse(message=ErrorMessage.INVALID_PLAYLIST_REORDER)

        self._repository.execute("DELETE FROM playlist_tracks WHERE playlist_id = ?", (playlist_id,))
        for position, track_id in enumerate(ordered_track_ids):
            self._repository.execute(
                "INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (?, ?, ?)",
                (playlist_id, track_id, position),
            )

        return SuccessResponse[dict[str, int]](
            message=SuccessMessage.PLAYLIST_TRACKS_UPDATED,
            data={"playlist_id": playlist_id, "track_count": len(ordered_track_ids)},
        )

    def get_playlist_track_ids(self, playlist_id: int) -> list[int]:
        rows = self._repository.fetch_all(
            "SELECT track_id FROM playlist_tracks WHERE playlist_id = ? ORDER BY position ASC",
            (playlist_id,),
        )
        return [int(row[0]) for row in rows]

    def _playlist_exists(self, playlist_id: int) -> bool:
        row = self._repository.fetch_one("SELECT 1 FROM playlists WHERE id = ? LIMIT 1", (playlist_id,))
        return row is not None

    def _track_exists(self, track_id: int) -> bool:
        row = self._repository.fetch_one("SELECT 1 FROM tracks WHERE id = ? LIMIT 1", (track_id,))
        return row is not None

    def _next_position(self, playlist_id: int) -> int:
        row = self._repository.fetch_one(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM playlist_tracks WHERE playlist_id = ?",
            (playlist_id,),
        )
        return int(row[0]) if row is not None else 0

    def _normalize_positions(self, playlist_id: int) -> None:
        ordered_ids = self.get_playlist_track_ids(playlist_id)
        self._repository.execute("DELETE FROM playlist_tracks WHERE playlist_id = ?", (playlist_id,))
        for position, track_id in enumerate(ordered_ids):
            self._repository.execute(
                "INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (?, ?, ?)",
                (playlist_id, track_id, position),
            )
