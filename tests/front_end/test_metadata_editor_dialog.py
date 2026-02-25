from pathlib import Path

from PyQt6.QtGui import QColor, QImage

from app.front_end.metadata_editor_dialog import MetadataEditorDialog


def _write_png(path: Path) -> None:
    image = QImage(4, 4, QImage.Format.Format_RGB32)
    image.fill(QColor("#3A6EA5"))
    assert image.save(str(path), "PNG")


def test_dialog_uses_explicit_labels_and_contrast_style(qtbot):
    dialog = MetadataEditorDialog()
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Edit Metadata"
    assert dialog.title_edit.placeholderText() == "Song title"
    assert dialog.artist_edit.placeholderText() == "Primary artist"
    assert dialog.album_edit.placeholderText() == "Album name"
    assert dialog.genre_edit.placeholderText() == "Genre"
    assert "QLabel" in dialog.styleSheet()
    assert "color: #DCE4F2;" in dialog.styleSheet()


def test_changed_values_returns_only_mutated_fields(qtbot):
    dialog = MetadataEditorDialog()
    qtbot.addWidget(dialog)

    dialog.set_values_from_metadata(
        {
            "title": "Song A",
            "artist": "Artist A",
            "album": "Album A",
            "genre": "Rock",
        }
    )

    dialog.title_edit.setText("Song B")
    dialog.album_edit.setText("")

    assert dialog.changed_values() == {"title": "Song B", "album": ""}


def test_changed_values_returns_empty_dict_when_no_changes(qtbot):
    dialog = MetadataEditorDialog()
    qtbot.addWidget(dialog)

    dialog.set_values_from_metadata(
        {
            "title": "Song A",
            "artist": "Artist A",
            "album": "Album A",
            "genre": "Rock",
        }
    )

    assert dialog.changed_values() == {}


def test_set_pending_artwork_replacement_sets_replace_action(qtbot, tmp_path):
    dialog = MetadataEditorDialog()
    qtbot.addWidget(dialog)
    image_path = tmp_path / "cover.png"
    _write_png(image_path)

    dialog.set_pending_artwork_replacement(str(image_path))

    assert dialog.artwork_change_request() == {"action": "replace", "image_path": str(image_path)}


def test_mark_artwork_for_removal_sets_remove_action(qtbot):
    dialog = MetadataEditorDialog()
    qtbot.addWidget(dialog)

    dialog.mark_artwork_for_removal()

    assert dialog.artwork_change_request() == {"action": "remove"}
