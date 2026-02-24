from app.back_end.services.playback_service import PlaybackService
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class _FakePlayerBackend:
    def __init__(self) -> None:
        self.play_called = 0
        self.pause_called = 0
        self.last_position: int | None = None
        self.last_speed: float | None = None

    def play(self) -> None:
        self.play_called += 1

    def pause(self) -> None:
        self.pause_called += 1

    def setPosition(self, position_ms: int) -> None:
        self.last_position = position_ms

    def setPlaybackRate(self, rate: float) -> None:
        self.last_speed = rate


class _FailingPlayerBackend(_FakePlayerBackend):
    def play(self) -> None:
        raise RuntimeError("player failed")


def test_play_returns_success_and_calls_backend():
    backend = _FakePlayerBackend()
    service = PlaybackService(backend)

    response = service.play()

    assert response.status is True
    assert response.message is SuccessMessage.PLAYBACK_STARTED
    assert response.data == {"action": "play"}
    assert backend.play_called == 1


def test_pause_returns_success_and_calls_backend():
    backend = _FakePlayerBackend()
    service = PlaybackService(backend)

    response = service.pause()

    assert response.status is True
    assert response.message is SuccessMessage.PLAYBACK_PAUSED
    assert response.data == {"action": "pause"}
    assert backend.pause_called == 1


def test_seek_returns_success_for_valid_position():
    backend = _FakePlayerBackend()
    service = PlaybackService(backend)

    response = service.seek(42_000)

    assert response.status is True
    assert response.message is SuccessMessage.SEEK_COMPLETED
    assert response.data == {"position_ms": 42_000}
    assert backend.last_position == 42_000


def test_seek_returns_error_for_negative_position():
    backend = _FakePlayerBackend()
    service = PlaybackService(backend)

    response = service.seek(-1)

    assert response.status is False
    assert response.message is ErrorMessage.INVALID_SEEK_POSITION
    assert response.data is None
    assert backend.last_position is None


def test_set_playback_speed_returns_success_for_valid_rate():
    backend = _FakePlayerBackend()
    service = PlaybackService(backend)

    response = service.set_playback_speed(1.25)

    assert response.status is True
    assert response.message is SuccessMessage.PLAYBACK_SPEED_UPDATED
    assert response.data == {"playback_speed": 1.25}
    assert backend.last_speed == 1.25


def test_set_playback_speed_returns_error_for_out_of_range_rate():
    backend = _FakePlayerBackend()
    service = PlaybackService(backend)

    response = service.set_playback_speed(10.0)

    assert response.status is False
    assert response.message is ErrorMessage.INVALID_PLAYBACK_SPEED
    assert response.data is None
    assert backend.last_speed is None


def test_play_returns_error_when_backend_raises():
    service = PlaybackService(_FailingPlayerBackend())

    response = service.play()

    assert response.status is False
    assert response.message is ErrorMessage.PLAYBACK_OPERATION_FAILED
    assert response.data is None
