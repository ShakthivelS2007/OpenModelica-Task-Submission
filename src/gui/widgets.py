"""Reusable composite widgets for the simulation launcher GUI."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget


class ExecutableSelector(QWidget):
    """A labeled file picker: a read-only line edit plus a Browse button."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._line_edit = QLineEdit(self)
        self._line_edit.setPlaceholderText("Path to OpenModelica model executable...")
        self._line_edit.setReadOnly(True)

        browse_button = QPushButton("Browse...", self)
        browse_button.clicked.connect(self._on_browse)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._line_edit)
        layout.addWidget(browse_button)

    def _on_browse(self) -> None:
        """Open a file dialog and store the chosen path."""
        path, _ = QFileDialog.getOpenFileName(self, "Select Model Executable")
        if path:
            self._line_edit.setText(path)

    def path(self) -> str:
        """Return the currently selected executable path."""
        return self._line_edit.text()
