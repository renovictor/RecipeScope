from __future__ import annotations

import logging
import sys
import traceback

from PySide6.QtWidgets import QMessageBox


def install_exception_handler(logger: logging.Logger) -> None:
    def _handler(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        details = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        logger.error("Unhandled exception:\n%s", details)
        QMessageBox.critical(
            None,
            "Unhandled Error",
            "RecipeScope encountered an unexpected error.\n\n"
            "See log file for details.",
        )

    sys.excepthook = _handler
