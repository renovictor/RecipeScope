from __future__ import annotations

import pandas as pd
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QWidget


class SummaryPanel(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Recipe Summary", parent)
        self.total_time = QLabel("0 s")
        self.max_power = QLabel("0 W")
        self.points = QLabel("0")
        form = QFormLayout(self)
        form.addRow("Total Time:", self.total_time)
        form.addRow("Peak Power:", self.max_power)
        form.addRow("Waveform Points:", self.points)

    def update_summary(self, dataframe: pd.DataFrame) -> None:
        if dataframe.empty:
            self.total_time.setText("0 s")
            self.max_power.setText("0 W")
            self.points.setText("0")
            return
        self.total_time.setText(f"{dataframe['time_s'].max():.6f} s")
        self.max_power.setText(f"{dataframe['power_w'].max():.3f} W")
        self.points.setText(str(len(dataframe.index)))
