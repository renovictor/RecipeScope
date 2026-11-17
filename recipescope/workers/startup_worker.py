from __future__ import annotations

import importlib.util

from PySide6.QtCore import QObject, Signal, Slot


class StartupWorker(QObject):
    finished = Signal(dict)

    OPTIONAL_MODULES = [
        "numpy",
        "PIL",
        "docx",
        "guardian_tlog",
        "jsonl_to_excel",
        "serial",
    ]

    @Slot()
    def run(self) -> None:
        status = {}
        for module in self.OPTIONAL_MODULES:
            status[module] = importlib.util.find_spec(module) is not None
        self.finished.emit(status)
