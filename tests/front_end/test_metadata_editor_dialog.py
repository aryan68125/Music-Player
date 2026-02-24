from app.front_end.metadata_editor_dialog import MetadataEditorDialog


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
