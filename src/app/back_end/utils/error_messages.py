from enum import Enum


class ErrorMessage(str, Enum):
    UNKNOWN_ERROR = "An unknown error occurred."
    INVALID_SEEK_POSITION = "Invalid seek position."
    INVALID_PLAYBACK_SPEED = "Invalid playback speed."
    PLAYBACK_OPERATION_FAILED = "Playback operation failed."
    INVALID_REPEAT_MODE = "Invalid repeat mode."
    INVALID_SHUFFLE_FLAG = "Invalid shuffle flag."
    TRACK_NOT_FOUND_IN_QUEUE = "Track not found in queue."
    TRACK_NOT_FOUND = "Track not found."
