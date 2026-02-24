from PyQt6.QtTest import QSignalSpy

from app.front_end.now_playing_bar import NowPlayingBar


def test_seek_slider_defers_seek_until_release(qtbot):
    widget = NowPlayingBar()
    qtbot.addWidget(widget)
    widget.set_track_duration_ms(120_000)
    spy = QSignalSpy(widget.seek_requested)

    widget.start_seek_drag()
    widget.drag_seek_to(45_000)

    assert len(spy) == 0

    widget.end_seek_drag()

    assert len(spy) == 1
    assert spy[0][0] == 45_000


def test_set_playing_updates_button_label(qtbot):
    widget = NowPlayingBar()
    qtbot.addWidget(widget)

    widget.set_playing(True)
    assert widget.play_pause_button.text() == "Pause"

    widget.set_playing(False)
    assert widget.play_pause_button.text() == "Play"


def test_control_buttons_emit_expected_signals(qtbot):
    widget = NowPlayingBar()
    qtbot.addWidget(widget)
    prev_spy = QSignalSpy(widget.previous_requested)
    play_spy = QSignalSpy(widget.play_pause_requested)
    next_spy = QSignalSpy(widget.next_requested)

    widget.previous_button.click()
    widget.play_pause_button.click()
    widget.next_button.click()

    assert len(prev_spy) == 1
    assert len(play_spy) == 1
    assert len(next_spy) == 1


def test_speed_selection_emits_float_rate(qtbot):
    widget = NowPlayingBar()
    qtbot.addWidget(widget)
    spy = QSignalSpy(widget.playback_speed_requested)

    widget.speed_combo.setCurrentText("1.25x")

    assert len(spy) == 1
    assert float(spy[0][0]) == 1.25
