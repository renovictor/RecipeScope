from __future__ import annotations

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget


class WaveformPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def plot_waveform(self, dataframe: pd.DataFrame, title: str = "Recipe Power Waveform") -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if dataframe.empty:
            ax.set_title("No waveform available")
            self.canvas.draw_idle()
            return
        ax.plot(dataframe["time_s"], dataframe["power_w"], color="#1f77b4", linewidth=1.5)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Power (W)")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw_idle()
