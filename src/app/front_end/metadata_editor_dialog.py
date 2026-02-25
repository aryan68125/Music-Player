from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class MetadataEditorDialog(QDialog):
    EDITABLE_FIELDS = ("title", "artist", "album", "genre")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Metadata")
        self.resize(520, 360)

        self._initial_values: dict[str, str] = {field: "" for field in self.EDITABLE_FIELDS}
        self._pending_artwork_path: str | None = None
        self._pending_remove_artwork = False

        self.title_edit = QLineEdit()
        self.artist_edit = QLineEdit()
        self.album_edit = QLineEdit()
        self.genre_edit = QLineEdit()

        self.title_edit.setPlaceholderText("Song title")
        self.artist_edit.setPlaceholderText("Primary artist")
        self.album_edit.setPlaceholderText("Album name")
        self.genre_edit.setPlaceholderText("Genre")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.addRow("Title", self.title_edit)
        form.addRow("Artist", self.artist_edit)
        form.addRow("Album", self.album_edit)
        form.addRow("Genre", self.genre_edit)

        self.artwork_label = QLabel("No artwork")
        self.artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artwork_label.setFixedSize(132, 132)
        self.artwork_label.setObjectName("artworkPreview")

        self.replace_artwork_button = QPushButton("Replace Artwork")
        self.remove_artwork_button = QPushButton("Remove Artwork")
        self.replace_artwork_button.clicked.connect(self._choose_replacement_artwork)
        self.remove_artwork_button.clicked.connect(self.mark_artwork_for_removal)

        artwork_controls = QVBoxLayout()
        artwork_controls.setContentsMargins(0, 0, 0, 0)
        artwork_controls.setSpacing(8)
        artwork_controls.addWidget(self.replace_artwork_button)
        artwork_controls.addWidget(self.remove_artwork_button)
        artwork_controls.addStretch(1)

        artwork_row = QHBoxLayout()
        artwork_row.setContentsMargins(0, 0, 0, 0)
        artwork_row.setSpacing(12)
        artwork_row.addWidget(self.artwork_label)
        artwork_row.addLayout(artwork_controls, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addLayout(artwork_row)
        layout.addWidget(buttons)
        self._apply_theme()

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

    def set_artwork_bytes(self, image_data: bytes | None) -> None:
        self._pending_artwork_path = None
        self._pending_remove_artwork = False
        self._set_artwork_preview(image_data)

    def set_pending_artwork_replacement(self, image_path: str) -> bool:
        path = Path(image_path)
        if not path.exists() or not path.is_file():
            return False

        image_data = path.read_bytes()
        pixmap = QPixmap()
        if not pixmap.loadFromData(image_data):
            return False

        self._pending_artwork_path = str(path)
        self._pending_remove_artwork = False
        self._set_artwork_preview(image_data)
        return True

    def mark_artwork_for_removal(self) -> None:
        self._pending_artwork_path = None
        self._pending_remove_artwork = True
        self._set_artwork_preview(None)

    def artwork_change_request(self) -> dict[str, str] | None:
        if self._pending_artwork_path:
            return {"action": "replace", "image_path": self._pending_artwork_path}
        if self._pending_remove_artwork:
            return {"action": "remove"}
        return None

    def _choose_replacement_artwork(self) -> None:
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Artwork",
            str(Path.home()),
            "Image Files (*.jpg *.jpeg *.png)",
        )
        if not image_path:
            return

        if not self.set_pending_artwork_replacement(image_path):
            QMessageBox.warning(self, "Invalid Image", "Select a valid JPG or PNG image.")

    def _set_artwork_preview(self, image_data: bytes | None) -> None:
        if image_data:
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                scaled = pixmap.scaled(
                    self.artwork_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.artwork_label.setPixmap(scaled)
                self.artwork_label.setText("")
                return

        self.artwork_label.setPixmap(QPixmap())
        self.artwork_label.setText("No artwork")

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background: #111722;
                color: #E7ECF3;
            }
            QLabel {
                color: #DCE4F2;
                font-weight: 600;
            }
            QLineEdit {
                background: #1B2638;
                color: #E7ECF3;
                border: 1px solid #324661;
                border-radius: 6px;
                padding: 6px 8px;
            }
            QPushButton {
                background: #243247;
                color: #E7ECF3;
                border: 1px solid #31435E;
                border-radius: 8px;
                padding: 6px 10px;
            }
            #artworkPreview {
                background: #1B2638;
                border: 1px solid #324661;
                border-radius: 10px;
                color: #AEBAD0;
            }
            """
        )
