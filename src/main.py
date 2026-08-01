"""Entry point for the OpenModelica Simulation Launcher application."""

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> int:
    """Create the QApplication, show the main window, and start the event loop."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
