# OpenModelica Simulation Launcher

A desktop GUI, built with **Python 3.6+** and **PyQt6**, that launches a
compiled OpenModelica model executable with user-supplied start/stop
simulation times. Built as the FOSSEE screening task for the OpenModelica
project.

## What this repository contains

1. **Part 1 — The compiled model.** The `model/` folder holds the
   executable produced by building the `TwoConnectedTanks` OpenModelica
   model in OMEdit, plus every runtime file it depends on.
2. **Part 2 — The PyQt6 GUI.** The `src/` folder holds the desktop
   application that lets a user pick that executable, set a start time and
   a stop time, and run it.

## Project structure

```
openmodelica-pyqt-launcher/
├── src/
│   ├── main.py                 # Application entry point
│   ├── core/
│   │   ├── simulation_runner.py  # QProcess wrapper: launches the executable
│   │   └── validators.py         # Pure logic for the 0 <= start < stop < 5 rule
│   └── gui/
│       ├── main_window.py        # Main window: layout + event wiring
│       └── widgets.py            # Reusable ExecutableSelector widget
├── tests/
│   └── test_validators.py      # Unit tests for the validation logic
├── model/                      # Compiled OpenModelica executable + deps go here
├── docs/screenshots/           # App screenshots for this README
├── requirements.txt
└── README.md
```

The app follows an OOP separation of concerns:

- `SimulationRunner` (in `core/`) owns all process-launching logic and
  knows nothing about widgets — it communicates via Qt signals
  (`output_received`, `error_received`, `started`, `finished`).
- `ExecutableSelector` (in `gui/widgets.py`) is a small composite widget
  (line edit + browse button) that can be reused or tested independently.
- `MainWindow` (in `gui/main_window.py`) composes the above, wires signals
  to slots, and contains no process-handling logic itself.
- `validate_time_range` (in `core/validators.py`) is a pure function with
  no Qt dependency, so it's trivially unit-testable.

## Part 1 — Building the OpenModelica model

Do this on a Linux or Windows 10/11 machine with OpenModelica installed:

1. Install OpenModelica from https://openmodelica.org/download/download-windows/
   or the Linux equivalent for your distro.
2. Open **OMEdit** (bundled with OpenModelica).
3. Load the provided model package (`File > Open Model/Library File(s)`).
4. Select the `TwoConnectedTanks` model and click **Build** (the hammer
   icon, or right-click the model → *Build*). This compiles the model and
   generates an executable (`TwoConnectedTanks` / `TwoConnectedTanks.exe`)
   plus its dependent files in the working directory.
5. Copy that executable and every generated file it needs at runtime into
   the `model/` folder of this repo (see `model/README.md` for the exact
   list).

Simulation start/stop times are passed to the executable at runtime as
command-line simulation flags, documented here:
https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/simulationflags.html#simflagoverride

This app calls the executable as:

```
<executable> -override=startTime=<start>,stopTime=<stop>
```

## Part 2 — Running the GUI

### Requirements

- Python 3.6+
- PyQt6

### Setup

```bash
python3 -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Run

```bash
cd src
python3 main.py
```

### Usage

1. Click **Browse...** and select the model executable from `model/`.
2. Set **Start time** and **Stop time** (integers). The app enforces
   `0 <= start time < stop time < 5`, per the task's test requirement, and
   shows a warning dialog if the values are invalid.
3. Click **Run Simulation**. Output and errors from the executable stream
   into the log panel in real time; the status label shows the exit code
   once the run completes.

## Running the tests

The validation logic has no GUI dependency, so it can be tested without a
display:

```bash
pip install pytest
pytest tests/ -v
```

## Notes on design choices

- **QProcess over `subprocess`**: `QProcess` integrates with Qt's event
  loop, so the simulation runs asynchronously and the GUI never freezes
  while the executable is running.
- **Read-only path field**: the executable path is only ever set via the
  file dialog, preventing typos in a path that must be exact.
- **Bounded spin boxes**: `QSpinBox` ranges are constrained at the widget
  level (`0` to `4`) in addition to the explicit validation function, so
  invalid values are hard to enter in the first place; the validator is
  still what actually enforces the rule and is what's unit-tested.
