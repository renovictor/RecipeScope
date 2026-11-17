from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from recipescope.constants import ASSETS_DIR
from recipescope.exception_handler import install_exception_handler
from recipescope.logging_config import configure_logging
from recipescope.ui.main_window import MainWindow
from recipescope.ui.splash_screen import create_splash
from recipescope.ui.styles import APP_STYLE


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    logger = configure_logging()
    install_exception_handler(logger)

    splash = create_splash(ASSETS_DIR / "ASM-logo-small.gif")
    splash.show()
    window = MainWindow(logger)
    window.show()
    splash.finish(window)
    return app.exec()
