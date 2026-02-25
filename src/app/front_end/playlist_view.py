from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class _ReorderableTrackList(QListWidget):
    order_changed = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

    def dropEvent(self, event) -> None:  # type: ignore[override]
        super().dropEvent(event)
        ordered_paths = []
        for index in range(self.count()):
            item = self.item(index)
            ordered_paths.append(item.data(Qt.ItemDataRole.UserRole))
        self.order_changed.emit(ordered_paths)


class PlaylistView(QWidget):
    track_activated = pyqtSignal(int)
    track_order_changed = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.list_widget = _ReorderableTrackList()
        self.list_widget.itemDoubleClicked.connect(self._emit_track_activated)
        self.list_widget.order_changed.connect(self.track_order_changed.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.list_widget)

    def set_tracks(self, track_paths: list[Path], display_titles: Mapping[str, str] | None = None) -> None:
        self.list_widget.clear()
        display_titles = display_titles or {}
        for path in track_paths:
            item = QListWidgetItem(display_titles.get(str(path)) or path.stem)
            item.setToolTip(str(path))
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.list_widget.addItem(item)

    def set_current_index(self, index: int) -> None:
        if 0 <= index < self.list_widget.count():
            self.list_widget.setCurrentRow(index)

    def current_index(self) -> int:
        return self.list_widget.currentRow()

    def _emit_track_activated(self, item: QListWidgetItem) -> None:
        self.track_activated.emit(self.list_widget.row(item))
