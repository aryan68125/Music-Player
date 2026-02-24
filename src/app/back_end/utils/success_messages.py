from enum import Enum


class SuccessMessage(str, Enum):
    GENERAL_SUCCESS = "Operation completed successfully."
    PLAYBACK_STARTED = "Playback started."
    PLAYBACK_PAUSED = "Playback paused."
    SEEK_COMPLETED = "Seek completed."
    PLAYBACK_SPEED_UPDATED = "Playback speed updated."
    QUEUE_MODE_UPDATED = "Queue mode updated."
    QUEUE_TRACK_RESOLVED = "Queue resolved next or previous track."
    TRACK_ADDED_TO_FAVORITES = "Track added to favorites."
