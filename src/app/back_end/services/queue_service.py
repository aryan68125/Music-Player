import random
from collections.abc import Sequence
from enum import Enum

from app.back_end.utils.class_method_response_models import ErrorResponse, MethodResponse, SuccessResponse
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class RepeatMode(str, Enum):
    OFF = "off"
    REPEAT_ONE = "repeat_one"
    REPEAT_ALL = "repeat_all"


class QueueService:
    def __init__(self, track_ids: Sequence[str]) -> None:
        self._original_order = list(track_ids)
        self._active_order = list(track_ids)
        self._repeat_mode = RepeatMode.OFF
        self._shuffle_enabled = False

    def set_repeat_mode(self, mode: str) -> MethodResponse[dict[str, str]]:
        try:
            resolved_mode = RepeatMode(mode)
        except ValueError:
            return ErrorResponse(message=ErrorMessage.INVALID_REPEAT_MODE)

        self._repeat_mode = resolved_mode
        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.QUEUE_MODE_UPDATED,
            data={"repeat_mode": self._repeat_mode.value},
        )

    def set_shuffle(self, enabled: bool, seed: int | None = None) -> MethodResponse[dict[str, bool]]:
        if not isinstance(enabled, bool):
            return ErrorResponse(message=ErrorMessage.INVALID_SHUFFLE_FLAG)

        self._shuffle_enabled = enabled
        if enabled:
            rng = random.Random(seed)
            self._active_order = list(self._original_order)
            rng.shuffle(self._active_order)
        else:
            self._active_order = list(self._original_order)

        return SuccessResponse[dict[str, bool]](
            message=SuccessMessage.QUEUE_MODE_UPDATED,
            data={"shuffle_enabled": self._shuffle_enabled},
        )

    def next_track(self, current_track_id: str) -> MethodResponse[dict[str, str | None]]:
        return self._resolve_neighbor(current_track_id=current_track_id, direction=1)

    def previous_track(self, current_track_id: str) -> MethodResponse[dict[str, str | None]]:
        return self._resolve_neighbor(current_track_id=current_track_id, direction=-1)

    def _resolve_neighbor(self, current_track_id: str, direction: int) -> MethodResponse[dict[str, str | None]]:
        if current_track_id not in self._active_order:
            return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND_IN_QUEUE)

        if self._repeat_mode == RepeatMode.REPEAT_ONE:
            return SuccessResponse[dict[str, str | None]](
                message=SuccessMessage.QUEUE_TRACK_RESOLVED,
                data={"track_id": current_track_id},
            )

        current_index = self._active_order.index(current_track_id)
        neighbor_index = current_index + direction

        if 0 <= neighbor_index < len(self._active_order):
            track_id = self._active_order[neighbor_index]
            return SuccessResponse[dict[str, str | None]](
                message=SuccessMessage.QUEUE_TRACK_RESOLVED,
                data={"track_id": track_id},
            )

        if self._repeat_mode == RepeatMode.REPEAT_ALL and self._active_order:
            wrap_index = 0 if direction > 0 else len(self._active_order) - 1
            return SuccessResponse[dict[str, str | None]](
                message=SuccessMessage.QUEUE_TRACK_RESOLVED,
                data={"track_id": self._active_order[wrap_index]},
            )

        return SuccessResponse[dict[str, str | None]](
            message=SuccessMessage.QUEUE_TRACK_RESOLVED,
            data={"track_id": None},
        )
