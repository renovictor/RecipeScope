from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from recipescope.models import RecipeStep


class RecipeTable(QTableWidget):
    COLUMNS = [
        "enabled",
        "step_name",
        "cycle_group",
        "repeat_count",
        "duration",
        "time_unit",
        "power",
        "power_unit",
        "mode",
        "notes",
    ]

    def __init__(self) -> None:
        super().__init__(0, len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.verticalHeader().setVisible(False)

    def set_steps(self, steps: list[RecipeStep]) -> None:
        self.setRowCount(0)
        for step in steps:
            row = self.rowCount()
            self.insertRow(row)
            self._set_row(row, step)

    def append_default_row(self) -> None:
        row = self.rowCount()
        self.insertRow(row)
        self._set_row(row, RecipeStep(step_name=f"Step {row + 1}", duration=1, power=0))

    def _set_row(self, row: int, step: RecipeStep) -> None:
        values = [
            str(step.enabled),
            step.step_name,
            step.cycle_group,
            str(step.repeat_count),
            str(step.duration),
            step.time_unit,
            str(step.power),
            step.power_unit,
            step.mode,
            step.notes,
        ]
        for col, value in enumerate(values):
            item = QTableWidgetItem(value)
            if col == 0:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if step.enabled else Qt.Unchecked)
            self.setItem(row, col, item)

    def get_steps(self) -> list[RecipeStep]:
        steps = []
        for row in range(self.rowCount()):
            enabled_item = self.item(row, 0)
            enabled = enabled_item.checkState() == Qt.Checked if enabled_item else True
            steps.append(
                RecipeStep(
                    enabled=enabled,
                    step_name=self._text(row, 1),
                    cycle_group=self._text(row, 2),
                    repeat_count=self._int(row, 3, 1),
                    duration=self._float(row, 4, 0.0),
                    time_unit=self._text(row, 5) or "ms",
                    power=self._float(row, 6, 0.0),
                    power_unit=self._text(row, 7) or "W",
                    mode=self._text(row, 8) or "CW",
                    notes=self._text(row, 9),
                )
            )
        return steps

    def _text(self, row: int, col: int) -> str:
        item = self.item(row, col)
        return item.text().strip() if item else ""

    def _float(self, row: int, col: int, default: float) -> float:
        try:
            return float(self._text(row, col))
        except ValueError:
            return default

    def _int(self, row: int, col: int, default: int) -> int:
        try:
            return int(float(self._text(row, col)))
        except ValueError:
            return default
