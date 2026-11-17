from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout

from recipescope.constants import POWER_UNITS, TIME_UNITS


class SettingsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.time_unit = QComboBox()
        self.time_unit.addItems(TIME_UNITS)
        self.power_unit = QComboBox()
        self.power_unit.addItems(POWER_UNITS)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QFormLayout(self)
        layout.addRow("Default time unit", self.time_unit)
        layout.addRow("Default power unit", self.power_unit)
        layout.addWidget(buttons)
