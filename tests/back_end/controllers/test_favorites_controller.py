from app.back_end.controllers.favorites_controller import FavoritesController
from app.back_end.data.database_handler.database import DatabaseHandler
from app.back_end.data.repositories.repository import Repository
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


def _create_track(db_handler: DatabaseHandler, path: str) -> int:
    connection = db_handler.connect()
    cursor = connection.execute(
        "INSERT INTO tracks (path, title, artist, album, duration_ms) VALUES (?, ?, ?, ?, ?)",
        (path, "Title", "Artist", "Album", 120_000),
    )
    connection.commit()
    return int(cursor.lastrowid)


def test_favoriting_track_adds_it_to_favorites_playlist(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = FavoritesController(repository)
    track_id = _create_track(db_handler, "/music/track1.mp3")

    response = controller.mark_favorite(track_id)

    assert response.status is True
    assert response.message is SuccessMessage.TRACK_ADDED_TO_FAVORITES
    assert response.data == {"track_id": track_id}
    assert controller.is_in_favorites(track_id) is True
    db_handler.close()


def test_favoriting_track_marks_is_favorite_flag(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = FavoritesController(repository)
    track_id = _create_track(db_handler, "/music/track2.mp3")

    controller.mark_favorite(track_id)

    row = repository.fetch_one("SELECT is_favorite FROM tracks WHERE id = ?", (track_id,))
    assert row == (1,)
    db_handler.close()


def test_favoriting_same_track_twice_does_not_duplicate_playlist_entries(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = FavoritesController(repository)
    track_id = _create_track(db_handler, "/music/track3.mp3")

    controller.mark_favorite(track_id)
    controller.mark_favorite(track_id)

    favorites_playlist_id = repository.fetch_one(
        "SELECT id FROM playlists WHERE name = ? AND kind = ?",
        ("Favorites", "smart"),
    )[0]
    row = repository.fetch_one(
        "SELECT COUNT(*) FROM playlist_tracks WHERE playlist_id = ? AND track_id = ?",
        (favorites_playlist_id, track_id),
    )
    assert row == (1,)
    db_handler.close()


def test_favoriting_unknown_track_returns_error(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = FavoritesController(repository)

    response = controller.mark_favorite(999)

    assert response.status is False
    assert response.message is ErrorMessage.TRACK_NOT_FOUND
    assert response.data is None
    db_handler.close()
