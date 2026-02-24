from app.back_end.controllers.playlist_controller import PlaylistController
from app.back_end.data.database_handler.database import DatabaseHandler
from app.back_end.data.repositories.repository import Repository
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


def _create_track(db_handler: DatabaseHandler, path: str) -> int:
    connection = db_handler.connect()
    cursor = connection.execute(
        "INSERT INTO tracks (path, title, artist, album, duration_ms) VALUES (?, ?, ?, ?, ?)",
        (path, "Title", "Artist", "Album", 180_000),
    )
    connection.commit()
    return int(cursor.lastrowid)


def test_create_playlist_persists_playlist_row(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = PlaylistController(repository)

    response = controller.create_playlist("Roadtrip")

    assert response.status is True
    assert response.message is SuccessMessage.PLAYLIST_CREATED
    playlist_id = response.data["playlist_id"]
    row = repository.fetch_one("SELECT name, kind FROM playlists WHERE id = ?", (playlist_id,))
    assert row == ("Roadtrip", "user")
    db_handler.close()


def test_rename_playlist_updates_name(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = PlaylistController(repository)
    playlist_id = controller.create_playlist("Old Name").data["playlist_id"]

    response = controller.rename_playlist(playlist_id, "New Name")

    assert response.status is True
    assert response.message is SuccessMessage.PLAYLIST_UPDATED
    row = repository.fetch_one("SELECT name FROM playlists WHERE id = ?", (playlist_id,))
    assert row == ("New Name",)
    db_handler.close()


def test_delete_playlist_removes_playlist_and_tracks(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = PlaylistController(repository)
    playlist_id = controller.create_playlist("Temporary").data["playlist_id"]
    track_id = _create_track(db_handler, "/music/delete_me.mp3")
    controller.add_track_to_playlist(playlist_id, track_id)

    response = controller.delete_playlist(playlist_id)

    assert response.status is True
    assert response.message is SuccessMessage.PLAYLIST_DELETED
    playlist_row = repository.fetch_one("SELECT 1 FROM playlists WHERE id = ?", (playlist_id,))
    assert playlist_row is None
    membership_row = repository.fetch_one(
        "SELECT COUNT(*) FROM playlist_tracks WHERE playlist_id = ?",
        (playlist_id,),
    )
    assert membership_row == (0,)
    db_handler.close()


def test_add_and_reorder_tracks_persists_track_order(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = PlaylistController(repository)
    playlist_id = controller.create_playlist("Order Test").data["playlist_id"]
    track_ids = [
        _create_track(db_handler, "/music/order_1.mp3"),
        _create_track(db_handler, "/music/order_2.mp3"),
        _create_track(db_handler, "/music/order_3.mp3"),
    ]

    controller.add_track_to_playlist(playlist_id, track_ids[0])
    controller.add_track_to_playlist(playlist_id, track_ids[1])
    controller.add_track_to_playlist(playlist_id, track_ids[2])
    reorder_response = controller.reorder_tracks(playlist_id, [track_ids[2], track_ids[0], track_ids[1]])

    assert reorder_response.status is True
    assert reorder_response.message is SuccessMessage.PLAYLIST_TRACKS_UPDATED
    assert controller.get_playlist_track_ids(playlist_id) == [track_ids[2], track_ids[0], track_ids[1]]
    db_handler.close()


def test_remove_track_updates_playlist_membership(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = PlaylistController(repository)
    playlist_id = controller.create_playlist("Remove Track").data["playlist_id"]
    track_ids = [
        _create_track(db_handler, "/music/remove_1.mp3"),
        _create_track(db_handler, "/music/remove_2.mp3"),
        _create_track(db_handler, "/music/remove_3.mp3"),
    ]
    controller.add_track_to_playlist(playlist_id, track_ids[0])
    controller.add_track_to_playlist(playlist_id, track_ids[1])
    controller.add_track_to_playlist(playlist_id, track_ids[2])

    response = controller.remove_track_from_playlist(playlist_id, track_ids[1])

    assert response.status is True
    assert response.message is SuccessMessage.PLAYLIST_TRACKS_UPDATED
    assert controller.get_playlist_track_ids(playlist_id) == [track_ids[0], track_ids[2]]
    db_handler.close()


def test_reorder_with_mismatched_track_set_returns_error(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = PlaylistController(repository)
    playlist_id = controller.create_playlist("Mismatch").data["playlist_id"]
    track_ids = [
        _create_track(db_handler, "/music/mismatch_1.mp3"),
        _create_track(db_handler, "/music/mismatch_2.mp3"),
    ]
    controller.add_track_to_playlist(playlist_id, track_ids[0])
    controller.add_track_to_playlist(playlist_id, track_ids[1])

    response = controller.reorder_tracks(playlist_id, [track_ids[0]])

    assert response.status is False
    assert response.message is ErrorMessage.INVALID_PLAYLIST_REORDER
    assert response.data is None
    db_handler.close()


def test_playlist_methods_return_error_for_unknown_playlist(tmp_path):
    db_handler = DatabaseHandler(db_path=tmp_path / "app.db")
    db_handler.initialize_schema()
    repository = Repository(db_handler)
    controller = PlaylistController(repository)
    track_id = _create_track(db_handler, "/music/unknown_playlist.mp3")

    response = controller.add_track_to_playlist(999, track_id)

    assert response.status is False
    assert response.message is ErrorMessage.PLAYLIST_NOT_FOUND
    assert response.data is None
    db_handler.close()
