from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class NowPlayingBar(QFrame):
    previous_requested = pyqtSignal()
    play_pause_requested = pyqtSignal()
    next_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    playback_speed_requested = pyqtSignal(float)
    shuffle_toggled = pyqtSignal(bool)
    repeat_mode_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._is_scrubbing = False
        self._repeat_modes = ["off", "repeat_all", "repeat_one"]
        self._repeat_mode_index = 0

        self.setObjectName("nowPlayingBar")
        self.setMinimumHeight(116)

        self.album_art_label = QLabel()
        self.album_art_label.setFixedSize(64, 64)
        self.album_art_label.setStyleSheet("background: #202735; border-radius: 8px;")

        self.track_title_label = QLabel("No track selected")
        self.track_title_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.track_artist_label = QLabel("-")
        self.track_artist_label.setStyleSheet("font-size: 12px; color: #9AA4B2;")

        self.previous_button = QPushButton("Prev")
        self.play_pause_button = QPushButton("Play")
        self.next_button = QPushButton("Next")

        self.current_time_label = QLabel("00:00")
        self.duration_label = QLabel("00:00")

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.50x", "0.75x", "1.00x", "1.25x", "1.50x", "2.00x"])
        self.speed_combo.setCurrentText("1.00x")

        self.shuffle_button = QPushButton("Shuffle")
        self.shuffle_button.setCheckable(True)

        self.repeat_button = QPushButton("Repeat: Off")

        self._wire_signals()
        self._build_layout()

    def _wire_signals(self) -> None:
        self.previous_button.clicked.connect(self.previous_requested.emit)
        self.play_pause_button.clicked.connect(self.play_pause_requested.emit)
        self.next_button.clicked.connect(self.next_requested.emit)

        self.seek_slider.sliderPressed.connect(self._begin_seek_drag)
        self.seek_slider.sliderReleased.connect(self._end_seek_drag_from_slider)
        self.seek_slider.valueChanged.connect(self._on_seek_value_changed)

        self.speed_combo.currentTextChanged.connect(self._emit_selected_speed)
        self.shuffle_button.toggled.connect(self.shuffle_toggled.emit)
        self.repeat_button.clicked.connect(self._cycle_repeat_mode)

    def _build_layout(self) -> None:
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        info_layout.addWidget(self.track_title_label)
        info_layout.addWidget(self.track_artist_label)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        controls_layout.addWidget(self.previous_button)
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addWidget(self.next_button)

        seek_layout = QHBoxLayout()
        seek_layout.setContentsMargins(0, 0, 0, 0)
        seek_layout.setSpacing(8)
        seek_layout.addWidget(self.current_time_label)
        seek_layout.addWidget(self.seek_slider)
        seek_layout.addWidget(self.duration_label)

        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        center_layout.addLayout(controls_layout)
        center_layout.addLayout(seek_layout)

        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.addWidget(self.speed_combo)
        right_layout.addWidget(self.shuffle_button)
        right_layout.addWidget(self.repeat_button)

        container = QHBoxLayout(self)
        container.setContentsMargins(16, 16, 16, 16)
        container.setSpacing(16)
        container.addWidget(self.album_art_label)
        container.addLayout(info_layout, 2)
        container.addLayout(center_layout, 4)
        container.addLayout(right_layout, 2)

    def _begin_seek_drag(self) -> None:
        self._is_scrubbing = True

    def _end_seek_drag_from_slider(self) -> None:
        self._is_scrubbing = False
        self.seek_requested.emit(self.seek_slider.value())

    def _on_seek_value_changed(self, value: int) -> None:
        self.current_time_label.setText(self._format_ms(value))

    def _emit_selected_speed(self, value: str) -> None:
        speed = value.replace("x", "").strip()
        try:
            self.playback_speed_requested.emit(float(speed))
        except ValueError:
            return

    def _cycle_repeat_mode(self) -> None:
        self._repeat_mode_index = (self._repeat_mode_index + 1) % len(self._repeat_modes)
        mode = self._repeat_modes[self._repeat_mode_index]
        label = {
            "off": "Repeat: Off",
            "repeat_all": "Repeat: All",
            "repeat_one": "Repeat: One",
        }[mode]
        self.repeat_button.setText(label)
        self.repeat_mode_requested.emit(mode)

    def set_playing(self, is_playing: bool) -> None:
        self.play_pause_button.setText("Pause" if is_playing else "Play")

    def set_track_info(self, title: str, artist: str) -> None:
        self.track_title_label.setText(title or "Unknown Title")
        self.track_artist_label.setText(artist or "Unknown Artist")

    def set_track_duration_ms(self, duration_ms: int) -> None:
        duration = max(0, int(duration_ms))
        self.seek_slider.setRange(0, duration)
        self.duration_label.setText(self._format_ms(duration))

    def set_playback_position_ms(self, position_ms: int) -> None:
        if self._is_scrubbing:
            return
        bounded = max(0, min(int(position_ms), self.seek_slider.maximum()))
        self.seek_slider.setValue(bounded)

    def set_album_art_bytes(self, image_data: bytes | None) -> None:
        pixmap = QPixmap()
        if image_data and pixmap.loadFromData(image_data):
            scaled = pixmap.scaled(
                self.album_art_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.album_art_label.setPixmap(scaled)
            return

        placeholder = QPixmap(self.album_art_label.size())
        placeholder.fill(Qt.GlobalColor.transparent)
        self.album_art_label.setPixmap(placeholder)

    def start_seek_drag(self) -> None:
        self._begin_seek_drag()

    def drag_seek_to(self, position_ms: int) -> None:
        bounded = max(0, min(int(position_ms), self.seek_slider.maximum()))
        self.seek_slider.setValue(bounded)

    def end_seek_drag(self) -> None:
        self._end_seek_drag_from_slider()

    @staticmethod
    def _format_ms(value: int) -> str:
        total_seconds = max(0, value // 1000)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return f"{minutes:02}:{seconds:02}"
