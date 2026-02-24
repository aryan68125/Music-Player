from app.back_end.app_bootstrap import AppBootstrap
from app.back_end.utils.success_messages import SuccessMessage


class _FakePlaybackBackend:
    def __init__(self) -> None:
        self.actions: list[tuple[str, object]] = []

    def play(self) -> None:
        self.actions.append(("play", None))

    def pause(self) -> None:
        self.actions.append(("pause", None))

    def setPosition(self, position_ms: int) -> None:
        self.actions.append(("seek", position_ms))

    def setPlaybackRate(self, rate: float) -> None:
        self.actions.append(("speed", rate))


def test_end_to_end_playlist_reorder_and_playback_flow(tmp_path):
    backend = _FakePlaybackBackend()
    app = AppBootstrap.create(db_path=tmp_path / "app.db", playback_backend=backend)

    try:
        t1 = app.register_track(path="/music/track-1.mp3", title="Track 1")
        t2 = app.register_track(path="/music/track-2.mp3", title="Track 2")
        t3 = app.register_track(path="/music/track-3.mp3", title="Track 3")

        playlist_response = app.playlists.create_playlist("E2E Mix")
        assert playlist_response.status is True
        playlist_id = int(playlist_response.data["playlist_id"])

        app.playlists.add_track_to_playlist(playlist_id, t1)
        app.playlists.add_track_to_playlist(playlist_id, t2)
        app.playlists.add_track_to_playlist(playlist_id, t3)

        reorder_response = app.playlists.reorder_tracks(playlist_id, [t3, t1, t2])
        assert reorder_response.status is True
        assert app.playlists.get_playlist_track_ids(playlist_id) == [t3, t1, t2]

        queue = app.build_queue_for_playlist(playlist_id)

        play_response = app.playback.play()
        assert play_response.status is True
        assert play_response.message is SuccessMessage.PLAYBACK_STARTED

        next_response = queue.next_track(str(t3))
        previous_response = queue.previous_track(str(t1))

        assert next_response.status is True
        assert next_response.data == {"track_id": str(t1)}
        assert previous_response.status is True
        assert previous_response.data == {"track_id": str(t3)}

        assert backend.actions[0] == ("play", None)
    finally:
        app.close()
