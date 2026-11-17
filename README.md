# RecipeScope

RecipeScope is a Windows desktop engineering application for defining semiconductor process recipes and expanding them into full time-domain power waveforms.

## Features
- Sequential recipe-step authoring with cycle-group repetition.
- Modes: CW, Pulse, Idle, Ramp Up, Ramp Down.
- Internal normalized units (seconds, watts) with display-unit flexibility.
- Waveform visualization with Matplotlib toolbar (zoom/pan/inspect).
- Project save/load (`*.rscp.json`).
- Data export: CSV, Excel (`.xlsx`), waveform image export (`.png`, `.svg`, `.pdf`).
- Recipe validation with explicit error and warning reporting.
- Rotating log files in `%LOCALAPPDATA%\RecipeScope\logs`.
- Optional dependency detection at startup.

## Runtime Requirements
Mandatory:
- Python 3.11+
- PySide6
- pandas
- openpyxl
- matplotlib

Optional (graceful if absent):
- NumPy
- Pillow/PIL
- python-docx
- guardian_tlog
- jsonl_to_excel
- pyserial

## Quick Start
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python main.py
```

Or run:
```bat
run_recipescope.bat
```

## Load Sample Recipe
Use **File -> Load Sample Recipe** to load `assets/sample_recipe.json`, then click **Expand Waveform**.

## Testing
```bat
python -m pytest -q
```

## Build Single EXE (Windows)
```bat
build_release.bat
```
Build configuration is in `RecipeScope.spec`. EXE naming is version-driven from `version.py`.

## Versioning
All version and release metadata are centralized in `version.py`. UI title, about dialog, build scripts, and executable naming consume this source.

## Project Layout
- `recipescope/models`: typed recipe data models.
- `recipescope/services`: expansion engine, validators, converters, I/O, exporters.
- `recipescope/ui`: PySide6 UI components and dialogs.
- `recipescope/workers`: background worker objects.
- `tests`: automated unit tests.
