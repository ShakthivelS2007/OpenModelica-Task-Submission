"""Main window for the OpenModelica Simulation Launcher application."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.simulation_runner import SimulationRunner
from core.validators import validate_time_range
from gui.widgets import ExecutableSelector

# Per the task spec: 0 <= start time < stop time < 5
MAX_STOP_TIME_EXCLUSIVE = 5


class MainWindow(QMainWindow):
    """Top-level window that lets a user configure and run an OpenModelica simulation."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OpenModelica Simulation Launcher")
        self.setMinimumWidth(560)

        self._runner = SimulationRunner(self)
        self._runner.output_received.connect(self._append_log)
        self._runner.error_received.connect(self._append_log)
        self._runner.started.connect(self._on_started)
        self._runner.finished.connect(self._on_finished)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct and lay out all child widgets."""
        self._executable_selector = ExecutableSelector(self)

        self._start_time_spin = QSpinBox(self)
        self._start_time_spin.setRange(0, MAX_STOP_TIME_EXCLUSIVE - 1)

        self._stop_time_spin = QSpinBox(self)
        self._stop_time_spin.setRange(1, MAX_STOP_TIME_EXCLUSIVE - 1)
        self._stop_time_spin.setValue(MAX_STOP_TIME_EXCLUSIVE - 1)

        self._run_button = QPushButton("Run Simulation", self)
        self._run_button.clicked.connect(self._on_run_clicked)

        self._status_label = QLabel("Idle", self)

        self._log_view = QTextEdit(self)
        self._log_view.setReadOnly(True)

        form_layout = QFormLayout()
        form_layout.addRow("Executable:", self._executable_selector)
        form_layout.addRow("Start time:", self._start_time_spin)
        form_layout.addRow("Stop time:", self._stop_time_spin)

        button_row = QHBoxLayout()
        button_row.addWidget(self._run_button)
        button_row.addWidget(self._status_label)
        button_row.addStretch(1)

        central_layout = QVBoxLayout()
        central_layout.addLayout(form_layout)
        central_layout.addLayout(button_row)
        central_layout.addWidget(QLabel("Output log:", self))
        central_layout.addWidget(self._log_view)

        central_widget = QWidget(self)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def _on_run_clicked(self) -> None:
        """Validate inputs and start the simulation process."""
        executable_path = self._executable_selector.path()
        start_time = self._start_time_spin.value()
        stop_time = self._stop_time_spin.value()

        if not executable_path:
            QMessageBox.warning(self, "Missing executable", "Please select a model executable.")
            return

        is_valid, message = validate_time_range(start_time, stop_time, MAX_STOP_TIME_EXCLUSIVE)
        if not is_valid:
            QMessageBox.warning(self, "Invalid time range", message)
            return

        self._log_view.clear()
        self._runner.run(executable_path, start_time, stop_time)

    def _on_started(self) -> None:
        """Update UI state when the simulation process starts."""
        self._status_label.setText("Running...")
        self._run_button.setEnabled(False)

    def _on_finished(self, exit_code: int) -> None:
        """Update UI state when the simulation process finishes."""
        self._status_label.setText(f"Finished (exit code {exit_code})")
        self._run_button.setEnabled(True)

    def _append_log(self, text: str) -> None:
        """Append a chunk of process output to the log view."""
        self._log_view.append(text)
