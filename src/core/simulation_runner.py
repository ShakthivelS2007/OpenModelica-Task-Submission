"""Runner that executes a compiled OpenModelica model executable via QProcess."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QProcess, pyqtSignal


class SimulationRunner(QObject):
    """Encapsulates launching and monitoring an OpenModelica model executable.

    Wraps ``QProcess`` to run a compiled OpenModelica simulation executable
    with explicit ``-startTime``/``-stopTime`` flags, emitting Qt signals so
    the GUI can react without blocking the event loop.
    """

    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    started = pyqtSignal()
    finished = pyqtSignal(int)  # exit code

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._process: Optional[QProcess] = None

    def is_running(self) -> bool:
        """Return True if a simulation process is currently running."""
        return (
            self._process is not None
            and self._process.state() != QProcess.ProcessState.NotRunning
        )

    def run(self, executable_path: str, start_time: int, stop_time: int) -> None:
        """Launch the executable with the given start/stop time flags.

        Passes ``-startTime`` and ``-stopTime`` as dedicated simulation
        flags (rather than via ``-override``, which some OpenModelica
        builds silently reject for these two experiment-level settings —
        confirmed against this project's compiled executable). Documented
        here:
        https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/simulationflags.html

        The process's working directory is set to the executable's own
        folder, since the generated executable looks for its companion
        files (e.g. ``<model>_init.xml``) relative to its current working
        directory, not relative to wherever the GUI itself was launched
        from.

        Args:
            executable_path: Absolute path to the OpenModelica model executable.
            start_time: Simulation start time (integer).
            stop_time: Simulation stop time (integer).
        """
        if self.is_running():
            self.error_received.emit("A simulation is already running.")
            return

        process = QProcess(self)
        process.setProgram(executable_path)
        process.setWorkingDirectory(str(Path(executable_path).parent))
        process.setArguments(
            [f"-startTime={start_time}", f"-stopTime={stop_time}"]
        )
        process.readyReadStandardOutput.connect(
            lambda: self.output_received.emit(
                bytes(process.readAllStandardOutput()).decode(errors="replace")
            )
        )
        process.readyReadStandardError.connect(
            lambda: self.error_received.emit(
                bytes(process.readAllStandardError()).decode(errors="replace")
            )
        )
        process.finished.connect(lambda code, _status: self.finished.emit(code))
        process.errorOccurred.connect(
            lambda err: self.error_received.emit(f"Process error: {err}")
        )

        self._process = process
        self._process.start()
        self.started.emit()

    def stop(self) -> None:
        """Terminate the running simulation process, if any."""
        if self.is_running():
            self._process.kill()
