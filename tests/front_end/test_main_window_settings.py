from __future__ import annotations

from pathlib import Path

from app.front_end import main_window as main_window_module


class _DummySignal:
    def connect(self, _callback) -> None:
        return None


class _FakeMediaPlayer:
    class PlaybackState:
        PlayingState = object()

    class MediaStatus:
        EndOfMedia = object()

    def __init__(self, *_args, **_kwargs) -> None:
        self.positionChanged = _DummySignal()
        self.durationChanged = _DummySignal()
        self.playbackStateChanged = _DummySignal()
        self.mediaStatusChanged = _DummySignal()

    def setAudioOutput(self, *_args, **_kwargs) -> None:
        return None

    def setSource(self, *_args, **_kwargs) -> None:
        return None

    def play(self) -> None:
        return None

    def pause(self) -> None:
        return None

    def setPosition(self, *_args, **_kwargs) -> None:
        return None

    def setPlaybackRate(self, *_args, **_kwargs) -> None:
        return None

    def playbackState(self):
        return None

    class _Source:
        @staticmethod
        def isEmpty() -> bool:
            return True

    def source(self):
        return self._Source()


class _FakeAudioOutput:
    def __init__(self, *_args, **_kwargs) -> None:
        self.volume = 0.0

    def setVolume(self, value: float) -> None:
        self.volume = value


def _build_window(qtbot, monkeypatch):
    monkeypatch.setattr(main_window_module, "QMediaPlayer", _FakeMediaPlayer)
    monkeypatch.setattr(main_window_module, "QAudioOutput", _FakeAudioOutput)

    window = main_window_module.MainWindow()
    qtbot.addWidget(window)
    return window


def test_settings_menu_has_autoplay_toggle_enabled_by_default(qtbot, monkeypatch):
    window = _build_window(qtbot, monkeypatch)

    assert window._autoplay_enabled is True
    assert window._autoplay_action.isCheckable()
    assert window._autoplay_action.isChecked() is True
    assert window._settings_button.menu() is window._settings_menu


def test_settings_menu_contains_edit_song_metadata_action(qtbot, monkeypatch):
    calls: list[bool] = []

    def _fake_open_metadata_editor(self) -> None:
        calls.append(True)

    monkeypatch.setattr(main_window_module.MainWindow, "_open_metadata_editor", _fake_open_metadata_editor)
    window = _build_window(qtbot, monkeypatch)

    edit_action = next(
        (action for action in window._settings_menu.actions() if action.text() == "Edit Song's Metadata"),
        None,
    )
    assert edit_action is not None

    edit_action.trigger()
    assert calls == [True]


def test_autoplay_toggle_action_updates_internal_flag(qtbot, monkeypatch):
    window = _build_window(qtbot, monkeypatch)

    window._autoplay_action.setChecked(False)
    assert window._autoplay_enabled is False

    window._autoplay_action.setChecked(True)
    assert window._autoplay_enabled is True


def test_add_songs_uses_autoplay_off_for_initial_track_load(qtbot, monkeypatch, tmp_path):
    window = _build_window(qtbot, monkeypatch)
    track_path = tmp_path / "song.mp3"
    track_path.touch()

    monkeypatch.setattr(window, "_select_music_files", lambda: [str(track_path)], raising=False)
    calls: list[tuple[int, bool]] = []
    monkeypatch.setattr(
        window,
        "_load_track_at_index",
        lambda index, autoplay: calls.append((index, autoplay)),
        raising=False,
    )
    window._autoplay_action.setChecked(False)

    window._add_songs()

    assert calls == [(0, False)]


def test_add_songs_uses_autoplay_on_for_initial_track_load(qtbot, monkeypatch, tmp_path):
    window = _build_window(qtbot, monkeypatch)
    track_path = tmp_path / "song.mp3"
    track_path.touch()

    monkeypatch.setattr(window, "_select_music_files", lambda: [str(track_path)], raising=False)
    calls: list[tuple[int, bool]] = []
    monkeypatch.setattr(
        window,
        "_load_track_at_index",
        lambda index, autoplay: calls.append((index, autoplay)),
        raising=False,
    )
    window._autoplay_action.setChecked(True)

    window._add_songs()

    assert calls == [(0, True)]


def test_select_music_files_uses_non_native_qt_dialog(qtbot, monkeypatch):
    window = _build_window(qtbot, monkeypatch)
    state: dict[str, object] = {}

    class _FakeFileDialog:
        class FileMode:
            ExistingFiles = "existing-files"

        class Option:
            DontUseNativeDialog = "dont-use-native"

        def __init__(self, parent, title: str, directory: str) -> None:
            state["parent"] = parent
            state["title"] = title
            state["directory"] = directory
            self._selected = ["/tmp/song-a.mp3", "/tmp/song-b.flac"]

        def setFileMode(self, mode) -> None:
            state["file_mode"] = mode

        def setNameFilter(self, name_filter: str) -> None:
            state["name_filter"] = name_filter

        def setOption(self, option, enabled: bool = True) -> None:
            state["option"] = option
            state["enabled"] = enabled

        def setStyleSheet(self, stylesheet: str) -> None:
            state["stylesheet"] = stylesheet

        def exec(self) -> int:
            return 1

        def selectedFiles(self) -> list[str]:
            return self._selected

    monkeypatch.setattr(main_window_module, "QFileDialog", _FakeFileDialog)

    selected = window._select_music_files()

    assert selected == ["/tmp/song-a.mp3", "/tmp/song-b.flac"]
    assert state["parent"] is window
    assert state["title"] == "Select songs"
    assert state["file_mode"] == _FakeFileDialog.FileMode.ExistingFiles
    assert "Audio Files" in str(state["name_filter"])
    assert state["option"] == _FakeFileDialog.Option.DontUseNativeDialog
    assert state["enabled"] is True
    assert "QFileDialog {" in str(state["stylesheet"])


def test_queue_uses_metadata_title_instead_of_file_name(qtbot, monkeypatch, tmp_path):
    window = _build_window(qtbot, monkeypatch)
    track_path = tmp_path / "track_file_name.mp3"
    track_path.touch()

    class _Response:
        status = True
        data = {"title": "Metadata Title"}

    class _FakeMetadataController:
        @staticmethod
        def read_metadata(_path: str):
            return _Response()

    window._metadata_controller = _FakeMetadataController()
    monkeypatch.setattr(window, "_select_music_files", lambda: [str(track_path)], raising=False)
    monkeypatch.setattr(window, "_load_track_at_index", lambda index, autoplay: None, raising=False)

    window._add_songs()

    assert window.playlist_view.list_widget.count() == 1
    assert window.playlist_view.list_widget.item(0).text() == "Metadata Title"


def test_queue_falls_back_to_file_stem_when_metadata_title_missing(qtbot, monkeypatch, tmp_path):
    window = _build_window(qtbot, monkeypatch)
    track_path = tmp_path / "track_file_name.mp3"
    track_path.touch()

    class _Response:
        status = True
        data = {"title": "   "}

    class _FakeMetadataController:
        @staticmethod
        def read_metadata(_path: str):
            return _Response()

    window._metadata_controller = _FakeMetadataController()
    monkeypatch.setattr(window, "_select_music_files", lambda: [str(track_path)], raising=False)
    monkeypatch.setattr(window, "_load_track_at_index", lambda index, autoplay: None, raising=False)

    window._add_songs()

    assert window.playlist_view.list_widget.count() == 1
    assert window.playlist_view.list_widget.item(0).text() == "track_file_name"
