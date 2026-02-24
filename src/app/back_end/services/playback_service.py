from typing import Protocol

from app.back_end.utils.class_method_response_models import ErrorResponse, MethodResponse, SuccessResponse
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class PlaybackBackendProtocol(Protocol):
    def play(self) -> None: ...

    def pause(self) -> None: ...

    def setPosition(self, position_ms: int) -> None: ...

    def setPlaybackRate(self, rate: float) -> None: ...


class PlaybackService:
    MIN_PLAYBACK_SPEED = 0.25
    MAX_PLAYBACK_SPEED = 3.0

    def __init__(self, player_backend: PlaybackBackendProtocol) -> None:
        self._player_backend = player_backend

    def play(self) -> MethodResponse[dict[str, str]]:
        try:
            self._player_backend.play()
        except Exception:
            return ErrorResponse(message=ErrorMessage.PLAYBACK_OPERATION_FAILED)
        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.PLAYBACK_STARTED,
            data={"action": "play"},
        )

    def pause(self) -> MethodResponse[dict[str, str]]:
        try:
            self._player_backend.pause()
        except Exception:
            return ErrorResponse(message=ErrorMessage.PLAYBACK_OPERATION_FAILED)
        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.PLAYBACK_PAUSED,
            data={"action": "pause"},
        )

    def seek(self, position_ms: int) -> MethodResponse[dict[str, int]]:
        if not isinstance(position_ms, int) or position_ms < 0:
            return ErrorResponse(message=ErrorMessage.INVALID_SEEK_POSITION)

        try:
            self._player_backend.setPosition(position_ms)
        except Exception:
            return ErrorResponse(message=ErrorMessage.PLAYBACK_OPERATION_FAILED)

        return SuccessResponse[dict[str, int]](
            message=SuccessMessage.SEEK_COMPLETED,
            data={"position_ms": position_ms},
        )

    def set_playback_speed(self, rate: float) -> MethodResponse[dict[str, float]]:
        if isinstance(rate, bool) or not isinstance(rate, int | float):
            return ErrorResponse(message=ErrorMessage.INVALID_PLAYBACK_SPEED)

        speed = float(rate)
        if speed < self.MIN_PLAYBACK_SPEED or speed > self.MAX_PLAYBACK_SPEED:
            return ErrorResponse(message=ErrorMessage.INVALID_PLAYBACK_SPEED)

        try:
            self._player_backend.setPlaybackRate(speed)
        except Exception:
            return ErrorResponse(message=ErrorMessage.PLAYBACK_OPERATION_FAILED)

        return SuccessResponse[dict[str, float]](
            message=SuccessMessage.PLAYBACK_SPEED_UPDATED,
            data={"playback_speed": speed},
        )
