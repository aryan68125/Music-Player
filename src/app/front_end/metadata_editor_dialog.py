from __future__ import annotations

from collections.abc import Mapping

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)


class MetadataEditorDialog(QDialog):
    EDITABLE_FIELDS = ("title", "artist", "album", "genre")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Metadata")
        self.resize(420, 220)

        self._initial_values: dict[str, str] = {field: "" for field in self.EDITABLE_FIELDS}

        self.title_edit = QLineEdit()
        self.artist_edit = QLineEdit()
        self.album_edit = QLineEdit()
        self.genre_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Title", self.title_edit)
        form.addRow("Artist", self.artist_edit)
        form.addRow("Album", self.album_edit)
        form.addRow("Genre", self.genre_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def set_values(self, title: str, artist: str, album: str, genre: str) -> None:
        self.set_values_from_metadata(
            {
                "title": title,
                "artist": artist,
                "album": album,
                "genre": genre,
            }
        )

    def set_values_from_metadata(self, metadata: Mapping[str, str]) -> None:
        normalized = {field: str(metadata.get(field, "")).strip() for field in self.EDITABLE_FIELDS}
        self._initial_values = dict(normalized)

        self.title_edit.setText(normalized["title"])
        self.artist_edit.setText(normalized["artist"])
        self.album_edit.setText(normalized["album"])
        self.genre_edit.setText(normalized["genre"])

    def changed_values(self) -> dict[str, str]:
        current = self.values()
        return {
            field: value
            for field, value in current.items()
            if self._initial_values.get(field, "") != value
        }

    def values(self) -> dict[str, str]:
        return {
            "title": self.title_edit.text().strip(),
            "artist": self.artist_edit.text().strip(),
            "album": self.album_edit.text().strip(),
            "genre": self.genre_edit.text().strip(),
        }
