from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen

from version import get_display_name


def create_splash(logo_path: Path) -> QSplashScreen:
    pixmap = QPixmap(str(logo_path)) if logo_path.exists() else QPixmap(480, 240)
    splash = QSplashScreen(pixmap)
    splash.showMessage(get_display_name(), alignment=Qt.AlignBottom | Qt.AlignCenter)
    return splash
