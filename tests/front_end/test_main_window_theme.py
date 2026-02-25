from app.front_end.main_window import build_app_stylesheet


def test_playback_speed_dropdown_popup_has_contrasting_colors():
    style = build_app_stylesheet()

    assert "QComboBox QAbstractItemView" in style
    assert "background: #1E2838;" in style
    assert "color: #E7ECF3;" in style
    assert "selection-background-color: #2F4E73;" in style
    assert "selection-color: #E7ECF3;" in style


def test_message_box_has_contrasting_text_and_background():
    style = build_app_stylesheet()

    assert "QMessageBox" in style
    assert "QMessageBox QLabel" in style
    assert "QMessageBox {"
    assert "background: #111722;" in style
    assert "QMessageBox QLabel {" in style
    assert "color: #E7ECF3;" in style
