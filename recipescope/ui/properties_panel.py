from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QWidget


class PropertiesPanel(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Step Properties", parent)
        self.labels = {
            "step_name": QLabel("-"),
            "mode": QLabel("-"),
            "duration": QLabel("-"),
            "power": QLabel("-"),
        }
        form = QFormLayout(self)
        form.addRow("Name:", self.labels["step_name"])
        form.addRow("Mode:", self.labels["mode"])
        form.addRow("Duration:", self.labels["duration"])
        form.addRow("Power:", self.labels["power"])

    def update_from_step(self, step: dict) -> None:
        self.labels["step_name"].setText(str(step.get("step_name", "-")))
        self.labels["mode"].setText(str(step.get("mode", "-")))
        self.labels["duration"].setText(f"{step.get('duration', '-')}")
        self.labels["power"].setText(f"{step.get('power', '-')}")
