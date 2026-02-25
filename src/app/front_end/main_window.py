from __future__ import annotations

from pathlib import Path

from mutagen import File as MutagenFile
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSizePolicy,
    QSplitter,
    QToolButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.back_end.controllers.metadata_controller import MetadataController
from app.back_end.services.rust_bridge import extract_artwork
from app.front_end.metadata_editor_dialog import MetadataEditorDialog
from app.front_end.now_playing_bar import NowPlayingBar
from app.front_end.playlist_view import PlaylistView


def build_app_stylesheet() -> str:
    return """
            QMainWindow {
                background: #0F131A;
                color: #E7ECF3;
            }
            QLabel {
                color: #E7ECF3;
            }
            QListWidget {
                background: #151B24;
                border: 1px solid #263041;
                border-radius: 8px;
                color: #DEE6F2;
            }
            QToolBar {
                background: #121925;
                border: 1px solid #263041;
                border-radius: 8px;
                spacing: 8px;
                padding: 6px;
            }
            QToolButton {
                background: #243247;
                color: #E7ECF3;
                border: 1px solid #31435E;
                border-radius: 8px;
                padding: 6px 10px;
            }
            #nowPlayingBar {
                background: #151B24;
                border: 1px solid #263041;
                border-radius: 12px;
            }
            QPushButton {
                background: #243247;
                color: #E7ECF3;
                border: 1px solid #31435E;
                border-radius: 8px;
                padding: 6px 10px;
            }
            QPushButton:checked {
                background: #2F4E73;
            }
            QComboBox {
                background: #1E2838;
                color: #E7ECF3;
                border: 1px solid #31435E;
                border-radius: 8px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView {
                background: #1E2838;
                color: #E7ECF3;
                border: 1px solid #31435E;
                selection-background-color: #2F4E73;
                selection-color: #E7ECF3;
            }
            QMessageBox {
                background: #111722;
                color: #E7ECF3;
            }
            QMessageBox QLabel {
                color: #E7ECF3;
            }
            QSlider::groove:horizontal {
                height: 4px;
                border-radius: 2px;
                background: #2A3548;
            }
            QSlider::handle:horizontal {
                width: 14px;
                margin: -6px 0;
                border-radius: 7px;
                background: #E7ECF3;
            }
            """


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Music Player")
        self.resize(1180, 760)

        self._track_paths: list[Path] = []
        self._current_index: int | None = None

        self._autoplay_enabled = True
        self._settings_menu: QMenu | None = None
        self._settings_button: QToolButton | None = None
        self._autoplay_action: QAction | None = None

        self._metadata_controller = MetadataController()

        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.7)

        self._build_toolbar()
        self._build_ui()
        self._wire_player_signals()
        self._apply_theme()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        add_action = QAction("Add Songs", self)
        add_action.triggered.connect(self._add_songs)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Metadata", self)
        edit_action.triggered.connect(self._open_metadata_editor)
        toolbar.addAction(edit_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        settings_menu = QMenu("Settings", self)
        autoplay_action = QAction("Autoplay newly added songs", self)
        autoplay_action.setCheckable(True)
        autoplay_action.setChecked(True)
        autoplay_action.toggled.connect(self._on_autoplay_toggled)
        settings_menu.addAction(autoplay_action)

        settings_button = QToolButton(self)
        settings_button.setText("Settings")
        settings_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        settings_button.setMenu(settings_menu)
        toolbar.addWidget(settings_button)

        self._settings_menu = settings_menu
        self._settings_button = settings_button
        self._autoplay_action = autoplay_action

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 12, 16, 12)
        root_layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        sidebar = QListWidget()
        sidebar.addItems(["Library", "Favorites", "Playlists"])
        sidebar.setFixedWidth(220)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        content_layout.addWidget(QLabel("Now Playing Queue"))

        self.playlist_view = PlaylistView()
        content_layout.addWidget(self.playlist_view)

        splitter.addWidget(sidebar)
        splitter.addWidget(content)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.now_playing_bar = NowPlayingBar()

        root_layout.addWidget(splitter, 1)
        root_layout.addWidget(self.now_playing_bar)
        self.setCentralWidget(root)

        self.playlist_view.track_activated.connect(self._play_track_at_index)

        self.now_playing_bar.previous_requested.connect(self._play_previous_track)
        self.now_playing_bar.next_requested.connect(self._play_next_track)
        self.now_playing_bar.play_pause_requested.connect(self._toggle_play_pause)
        self.now_playing_bar.seek_requested.connect(self._player.setPosition)
        self.now_playing_bar.playback_speed_requested.connect(self._player.setPlaybackRate)

    def _wire_player_signals(self) -> None:
        self._player.positionChanged.connect(self.now_playing_bar.set_playback_position_ms)
        self._player.durationChanged.connect(self.now_playing_bar.set_track_duration_ms)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)

    def _apply_theme(self) -> None:
        self.setStyleSheet(build_app_stylesheet())

    def _add_songs(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select songs",
            str(Path.home()),
            "Audio Files (*.mp3 *.m4a *.flac *.wav *.ogg *.aac *.opus *.aiff *.wma)",
        )
        if not files:
            return

        for file_path in files:
            path = Path(file_path)
            if path not in self._track_paths:
                self._track_paths.append(path)

        self.playlist_view.set_tracks(self._track_paths)
        if self._current_index is None and self._track_paths:
            self._load_track_at_index(0, autoplay=self._autoplay_enabled)

    def _toggle_play_pause(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        elif self._player.source().isEmpty() and self._track_paths:
            self._play_track_at_index(0)
        else:
            self._player.play()

    def _play_track_at_index(self, index: int) -> None:
        self._load_track_at_index(index, autoplay=True)

    def _load_track_at_index(self, index: int, autoplay: bool) -> None:
        if index < 0 or index >= len(self._track_paths):
            return

        self._current_index = index
        path = self._track_paths[index]
        self.playlist_view.set_current_index(index)
        self._player.setSource(QUrl.fromLocalFile(str(path)))

        if autoplay:
            self._player.play()
        else:
            self._player.pause()
            self.now_playing_bar.set_playing(False)

        metadata_response = self._metadata_controller.read_metadata(str(path))
        title = path.stem
        artist = "Local File"
        if metadata_response.status and isinstance(metadata_response.data, dict):
            title = metadata_response.data.get("title") or title
            artist = metadata_response.data.get("artist") or artist

        self.now_playing_bar.set_track_info(title, artist)
        self._update_album_art(path)

    def _on_autoplay_toggled(self, enabled: bool) -> None:
        self._autoplay_enabled = bool(enabled)

    def _play_next_track(self) -> None:
        if self._current_index is None or not self._track_paths:
            return
        if self._current_index + 1 >= len(self._track_paths):
            return
        self._play_track_at_index(self._current_index + 1)

    def _play_previous_track(self) -> None:
        if self._current_index is None or not self._track_paths:
            return
        if self._current_index - 1 < 0:
            return
        self._play_track_at_index(self._current_index - 1)

    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self.now_playing_bar.set_playing(state == QMediaPlayer.PlaybackState.PlayingState)

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._play_next_track()

    def _open_metadata_editor(self) -> None:
        if self._current_index is None:
            QMessageBox.information(self, "No Track", "Load and play a track before editing metadata.")
            return

        track_path = self._track_paths[self._current_index]
        metadata_response = self._metadata_controller.read_metadata(str(track_path))
        if not metadata_response.status or not isinstance(metadata_response.data, dict):
            QMessageBox.warning(
                self,
                "Metadata Error",
                metadata_response.message.value,
            )
            return

        dialog = MetadataEditorDialog(self)
        dialog.set_values_from_metadata(metadata_response.data)
        dialog.set_artwork_bytes(self._resolve_track_artwork_bytes(track_path))
        if not dialog.exec():
            return

        metadata_changes = dialog.changed_values()
        artwork_change = dialog.artwork_change_request()
        if not metadata_changes and not artwork_change:
            QMessageBox.information(self, "Metadata", "No metadata changes to save.")
            return

        success_messages: list[str] = []
        if metadata_changes:
            write_response = self._metadata_controller.update_metadata(str(track_path), metadata_changes)
            if not write_response.status:
                QMessageBox.warning(self, "Metadata Error", write_response.message.value)
                return
            success_messages.append(write_response.message.value)

        if artwork_change:
            if artwork_change["action"] == "replace":
                artwork_response = self._metadata_controller.replace_artwork(
                    str(track_path),
                    artwork_change["image_path"],
                )
            else:
                artwork_response = self._metadata_controller.remove_artwork(str(track_path))

            if not artwork_response.status:
                QMessageBox.warning(self, "Artwork Error", artwork_response.message.value)
                return
            success_messages.append(artwork_response.message.value)

        refreshed = self._metadata_controller.read_metadata(str(track_path))
        if refreshed.status and isinstance(refreshed.data, dict):
            self.now_playing_bar.set_track_info(
                refreshed.data.get("title") or track_path.stem,
                refreshed.data.get("artist") or "Local File",
            )

        self._update_album_art(track_path)
        QMessageBox.information(self, "Metadata Saved", "\n".join(success_messages))

    def _update_album_art(self, path: Path) -> None:
        self.now_playing_bar.set_album_art_bytes(self._resolve_track_artwork_bytes(path))

    def _resolve_track_artwork_bytes(self, path: Path) -> bytes | None:
        rust_response = extract_artwork(str(path))
        if rust_response.status and rust_response.data.get("artwork_bytes"):
            return rust_response.data["artwork_bytes"]

        embedded = self._extract_embedded_album_art(path)
        return embedded

    @staticmethod
    def _extract_embedded_album_art(path: Path) -> bytes | None:
        try:
            audio = MutagenFile(path)
            if audio is None:
                return None

            tags = getattr(audio, "tags", None)
            if tags:
                if "covr" in tags and tags["covr"]:
                    return bytes(tags["covr"][0])

                for key in tags.keys():
                    frame = tags[key]
                    frame_data = getattr(frame, "data", None)
                    if frame_data:
                        return bytes(frame_data)

            pictures = getattr(audio, "pictures", None)
            if pictures:
                return bytes(pictures[0].data)
        except Exception:
            return None

        return None
