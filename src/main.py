"""Application entrypoint for the PyQt music player."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from app.front_end.main_window import MainWindow


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
