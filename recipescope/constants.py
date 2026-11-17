from __future__ import annotations

from pathlib import Path

from version import APP_NAME

APP_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = APP_DIR / "assets"
DEFAULT_PROJECT_EXTENSION = ".rscp.json"
RECENT_FILES_PATH = Path.home() / "AppData" / "Local" / APP_NAME / "recent_files.json"
LOG_DIR = Path.home() / "AppData" / "Local" / APP_NAME / "logs"
SETTINGS_ORG = "ASM"
SETTINGS_APP = APP_NAME

TIME_UNITS = ("ns", "us", "µs", "ms", "s", "min")
POWER_UNITS = ("mW", "W", "kW")
MODES = ("CW", "Pulse", "Idle", "Ramp Up", "Ramp Down")
