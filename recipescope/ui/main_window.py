from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from recipescope.constants import ASSETS_DIR, DEFAULT_PROJECT_EXTENSION, RECENT_FILES_PATH
from recipescope.models import Recipe, RecipeStep
from recipescope.services import (
    ExcelExporter,
    ProjectIO,
    RecipeEngine,
    RecipeValidator,
    RecentFilesService,
    WaveformExporter,
)
from recipescope.ui.about_dialog import AboutDialog
from recipescope.ui.properties_panel import PropertiesPanel
from recipescope.ui.recipe_table import RecipeTable
from recipescope.ui.settings_dialog import SettingsDialog
from recipescope.ui.summary_panel import SummaryPanel
from recipescope.ui.waveform_panel import WaveformPanel
from version import APP_NAME, get_display_name


class MainWindow(QMainWindow):
    LOW_RES_OPTIONS = {
        "250uS": 250e-6,
        "333uS": 333e-6,
        "1mS": 1e-3,
        "10mS": 10e-3,
        "50mS": 50e-3,
        "100mS": 100e-3,
    }
    STRIKE_PLASMA_DELAY_S = 5e-3

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self.logger = logger
        self.engine = RecipeEngine()
        self.validator = RecipeValidator()
        self.project_io = ProjectIO()
        self.excel_exporter = ExcelExporter()
        self.waveform_exporter = WaveformExporter()
        self.recent_files = RecentFilesService(RECENT_FILES_PATH)
        self.current_recipe = Recipe()
        self.current_waveform = pd.DataFrame()
        self.current_project_path: str | None = None

        self.setWindowTitle(get_display_name())
        self.resize(1280, 820)
        self._build_ui()
        self._build_actions()

    def _build_ui(self) -> None:
        root = QWidget()
        main_layout = QVBoxLayout(root)

        controls = QHBoxLayout()
        self.btn_add = QPushButton("Add Step")
        self.btn_template = QPushButton("Template")
        self.btn_expand = QPushButton("Expand Waveform")
        self.low_res_combo = QComboBox()
        self.low_res_combo.addItems(list(self.LOW_RES_OPTIONS.keys()))
        self.low_res_combo.setCurrentText("10mS")
        controls.addWidget(self.btn_add)
        controls.addWidget(self.btn_template)
        controls.addWidget(self.btn_expand)
        controls.addWidget(QLabel("Low-Res Sampling:"))
        controls.addWidget(self.low_res_combo)
        controls.addStretch()
        main_layout.addLayout(controls)

        self.recipe_table = RecipeTable()
        self.recipe_table.setMinimumHeight(220)
        main_layout.addWidget(self.recipe_table)

        splitter = QSplitter(Qt.Horizontal)
        waveforms_container = QWidget()
        waveforms_layout = QVBoxLayout(waveforms_container)
        waveforms_layout.setContentsMargins(0, 0, 0, 0)
        waveforms_layout.setSpacing(8)

        self.waveform_panel = WaveformPanel()
        self.low_res_waveform_panel = WaveformPanel()
        waveforms_layout.addWidget(self.waveform_panel)
        waveforms_layout.addWidget(self.low_res_waveform_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.properties_panel = PropertiesPanel()
        self.summary_panel = SummaryPanel()
        right_layout.addWidget(self.properties_panel)
        right_layout.addWidget(self.summary_panel)
        right_layout.addStretch()

        splitter.addWidget(waveforms_container)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)
        self.setCentralWidget(root)

        self.btn_add.clicked.connect(self.recipe_table.append_default_row)
        self.btn_template.clicked.connect(self.load_template_recipe)
        self.btn_expand.clicked.connect(self.expand_waveform)
        self.low_res_combo.currentTextChanged.connect(self._refresh_low_res_waveform)
        self.recipe_table.itemSelectionChanged.connect(self._update_selected_properties)
        self.statusBar().showMessage(f"{APP_NAME} ready")

    def _build_actions(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("New", self.new_recipe)
        file_menu.addAction("Open...", self.open_project)
        file_menu.addAction("Save", self.save_project)
        file_menu.addAction("Save As...", self.save_project_as)
        file_menu.addSeparator()
        file_menu.addAction("Load Sample Recipe", self.load_sample_recipe)
        file_menu.addSeparator()
        file_menu.addAction("Export CSV...", self.export_csv)
        file_menu.addAction("Export Excel...", self.export_excel)
        file_menu.addAction("Export PNG...", lambda: self.export_waveform(".png"))
        file_menu.addAction("Export SVG...", lambda: self.export_waveform(".svg"))
        file_menu.addAction("Export PDF...", lambda: self.export_waveform(".pdf"))
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        tools_menu = self.menuBar().addMenu("&Tools")
        tools_menu.addAction("Settings", self.open_settings)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction("About", self.show_about)

    def _recipe_from_table(self) -> Recipe:
        return Recipe(name=self.current_recipe.name, steps=self.recipe_table.get_steps())

    def new_recipe(self) -> None:
        self.current_recipe = Recipe()
        self.current_project_path = None
        self.recipe_table.set_steps([])
        self.waveform_panel.plot_waveform(pd.DataFrame())
        self.low_res_waveform_panel.plot_waveform(pd.DataFrame())
        self.summary_panel.update_summary(pd.DataFrame())

    def load_sample_recipe(self) -> None:
        sample_path = ASSETS_DIR / "sample_recipe.json"
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        self.current_recipe = Recipe.from_dict(payload["recipe"])
        self.recipe_table.set_steps(self.current_recipe.steps)
        self.expand_waveform()

    def load_template_recipe(self) -> None:
        self.current_project_path = None
        self.current_waveform = pd.DataFrame()
        self.current_recipe = Recipe(
            name="Template Recipe",
            steps=[
                RecipeStep(
                    enabled=True,
                    step_name="depo",
                    cycle_group="a",
                    repeat_count=8,
                    duration=50,
                    time_unit="ms",
                    power=15,
                    power_unit="W",
                    mode="CW",
                ),
                RecipeStep(
                    enabled=True,
                    step_name="idle",
                    cycle_group="a",
                    repeat_count=8,
                    duration=150,
                    time_unit="ms",
                    power=0,
                    power_unit="W",
                    mode="CW",
                ),
                RecipeStep(
                    enabled=True,
                    step_name="trmnt",
                    cycle_group="a",
                    repeat_count=8,
                    duration=150,
                    time_unit="ms",
                    power=200,
                    power_unit="W",
                    mode="CW",
                ),
                RecipeStep(
                    enabled=True,
                    step_name="idle",
                    cycle_group="a",
                    repeat_count=8,
                    duration=650,
                    time_unit="ms",
                    power=0,
                    power_unit="W",
                    mode="CW",
                ),
            ],
        )
        self.recipe_table.set_steps(self.current_recipe.steps)
        self.waveform_panel.plot_waveform(pd.DataFrame())
        self.low_res_waveform_panel.plot_waveform(pd.DataFrame())
        self.summary_panel.update_summary(pd.DataFrame())
        self.statusBar().showMessage("Template loaded")

    def expand_waveform(self) -> None:
        recipe = self._recipe_from_table()
        validation = self.validator.validate(recipe)
        if not validation.is_valid:
            message = "\n".join(
                [
                    f"Row {err.row}: {err.message}" if err.row else err.message
                    for err in validation.errors
                ]
            )
            QMessageBox.warning(self, "Validation Error", message)
            return
        self.current_recipe = recipe
        self.current_waveform = self.engine.expand_recipe(recipe)
        self.waveform_panel.plot_waveform(self.current_waveform, "Recipe Power Waveform")
        self._refresh_low_res_waveform()
        self.summary_panel.update_summary(self.current_waveform)
        self.statusBar().showMessage("Waveform expanded successfully")

    def open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open RecipeScope Project", "", f"RecipeScope (*{DEFAULT_PROJECT_EXTENSION})"
        )
        if not path:
            return
        self.current_recipe = self.project_io.load_project(path)
        self.current_waveform = pd.DataFrame()
        self.current_project_path = path
        self.recipe_table.set_steps(self.current_recipe.steps)
        self.waveform_panel.plot_waveform(pd.DataFrame())
        self.low_res_waveform_panel.plot_waveform(pd.DataFrame())
        self.summary_panel.update_summary(pd.DataFrame())
        self.recent_files.add(path)
        self.statusBar().showMessage(f"Opened {path}")

    def save_project(self) -> None:
        if not self.current_project_path:
            self.save_project_as()
            return
        self.current_recipe = self._recipe_from_table()
        self.project_io.save_project(self.current_recipe, self.current_project_path)
        self.recent_files.add(self.current_project_path)
        self.statusBar().showMessage(f"Saved {self.current_project_path}")

    def save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save RecipeScope Project",
            f"recipe{DEFAULT_PROJECT_EXTENSION}",
            f"RecipeScope (*{DEFAULT_PROJECT_EXTENSION})",
        )
        if not path:
            return
        if not path.endswith(DEFAULT_PROJECT_EXTENSION):
            path = path + DEFAULT_PROJECT_EXTENSION
        self.current_project_path = path
        self.save_project()

    def export_csv(self) -> None:
        if self.current_waveform.empty:
            self.expand_waveform()
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV (*.csv)")
        if path:
            self.current_waveform.to_csv(path, index=False)

    def export_excel(self) -> None:
        if self.current_waveform.empty:
            self.expand_waveform()
        path, _ = QFileDialog.getSaveFileName(self, "Export Excel", "", "Excel (*.xlsx)")
        if path:
            self.excel_exporter.export(self.current_waveform, path)

    def export_waveform(self, ext: str) -> None:
        if self.current_waveform.empty:
            self.expand_waveform()
        path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export {ext.upper()}",
            "",
            f"{ext.upper()} (*{ext})",
        )
        if path:
            if not path.lower().endswith(ext):
                path = path + ext
            self.waveform_exporter.export(self.waveform_panel.figure, Path(path))

    def _update_selected_properties(self) -> None:
        row = self.recipe_table.currentRow()
        if row < 0:
            return
        step = {
            "step_name": self.recipe_table.item(row, 1).text() if self.recipe_table.item(row, 1) else "",
            "mode": self.recipe_table.item(row, 8).text() if self.recipe_table.item(row, 8) else "",
            "duration": self.recipe_table.item(row, 4).text() if self.recipe_table.item(row, 4) else "",
            "power": self.recipe_table.item(row, 6).text() if self.recipe_table.item(row, 6) else "",
        }
        self.properties_panel.update_from_step(step)

    def _refresh_low_res_waveform(self, *_: object) -> None:
        if self.current_waveform.empty:
            self.low_res_waveform_panel.plot_waveform(pd.DataFrame())
            return
        interval_s = self.LOW_RES_OPTIONS.get(self.low_res_combo.currentText(), 10e-3)
        reduced = self._downsample_waveform(self.current_waveform, interval_s)
        title = f"Recipe Power Waveform (Low Res: {self.low_res_combo.currentText()})"
        self.low_res_waveform_panel.plot_waveform(reduced, title)

    @staticmethod
    def _downsample_waveform(dataframe: pd.DataFrame, interval_s: float) -> pd.DataFrame:
        if dataframe.empty or interval_s <= 0:
            return dataframe.copy()

        columns = ["time_s", "power_w", "cycle_index"]
        if "cycle_index" not in dataframe.columns:
            trace = dataframe[["time_s", "power_w"]].copy()
            trace["cycle_index"] = 1
        else:
            trace = dataframe[columns].copy()
        trace = trace.reset_index(drop=True)

        trace["cycle_segment"] = (trace["cycle_index"] != trace["cycle_index"].shift()).cumsum()
        segment_ranges = trace.groupby("cycle_segment", sort=True)["time_s"].agg(["min", "max"])

        sample_times: list[float] = []
        for segment_order, (_, bounds) in enumerate(segment_ranges.iterrows()):
            start = float(bounds["min"])
            end = float(bounds["max"])
            if end <= start:
                sample_times.append(start)
                continue

            phase_offset = ((segment_order * 0.05) % 1.0) * interval_s
            current_time = start + phase_offset

            sample_times.append(start)
            while current_time <= end:
                sample_times.append(current_time)
                current_time += interval_s
            sample_times.append(end)

        # Keep duplicate timestamps deterministic so state changes at the same time
        # resolve to the last original row (e.g., high->low boundary should keep low).
        sampled = (
            trace.assign(_order=trace.index)
            .sort_values(["time_s", "_order"], kind="mergesort")
            .drop_duplicates(subset="time_s", keep="last")
            .drop(columns=["_order"])
        )
        sample_series = pd.Series(sample_times, dtype=float).drop_duplicates().sort_values()
        sample_frame = pd.DataFrame({"time_s": sample_series.to_list()})
        reduced = pd.merge_asof(
            sample_frame,
            sampled[["time_s", "power_w"]],
            on="time_s",
            direction="backward",
        )
        reduced["power_w"] = reduced["power_w"].ffill().fillna(0.0)

        # Simulate forward-power strike time: after each rising edge, measured
        # power remains near zero for a short delay before the commanded level.
        strike_delay = MainWindow.STRIKE_PLASMA_DELAY_S
        if strike_delay > 0:
            rising_edges = sampled.loc[
                (sampled["power_w"] > 0) & (sampled["power_w"].shift(fill_value=0) <= 0),
                "time_s",
            ].to_list()
            if rising_edges:
                strike_mask = pd.Series(False, index=reduced.index)
                for rise_time in rising_edges:
                    strike_mask = strike_mask | (
                        (reduced["time_s"] >= float(rise_time))
                        & (reduced["time_s"] < float(rise_time) + strike_delay)
                    )
                reduced.loc[strike_mask, "power_w"] = 0.0
        return reduced

    def open_settings(self) -> None:
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_about(self) -> None:
        AboutDialog(self).exec()
