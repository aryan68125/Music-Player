from enum import Enum


class ErrorMessage(str, Enum):
    UNKNOWN_ERROR = "An unknown error occurred."
    INVALID_SEEK_POSITION = "Invalid seek position."
    INVALID_PLAYBACK_SPEED = "Invalid playback speed."
    PLAYBACK_OPERATION_FAILED = "Playback operation failed."
