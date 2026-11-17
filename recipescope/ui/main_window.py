from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from recipescope.constants import ASSETS_DIR, DEFAULT_PROJECT_EXTENSION, RECENT_FILES_PATH
from recipescope.models import Recipe
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
        self.btn_expand = QPushButton("Expand Waveform")
        controls.addWidget(self.btn_add)
        controls.addWidget(self.btn_expand)
        controls.addStretch()
        main_layout.addLayout(controls)

        splitter = QSplitter(Qt.Horizontal)
        self.recipe_table = RecipeTable()
        self.waveform_panel = WaveformPanel()
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.properties_panel = PropertiesPanel()
        self.summary_panel = SummaryPanel()
        right_layout.addWidget(self.properties_panel)
        right_layout.addWidget(self.summary_panel)
        right_layout.addStretch()

        splitter.addWidget(self.recipe_table)
        splitter.addWidget(self.waveform_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        main_layout.addWidget(splitter)
        self.setCentralWidget(root)

        self.btn_add.clicked.connect(self.recipe_table.append_default_row)
        self.btn_expand.clicked.connect(self.expand_waveform)
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
        self.summary_panel.update_summary(pd.DataFrame())

    def load_sample_recipe(self) -> None:
        sample_path = ASSETS_DIR / "sample_recipe.json"
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        self.current_recipe = Recipe.from_dict(payload["recipe"])
        self.recipe_table.set_steps(self.current_recipe.steps)
        self.expand_waveform()

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
        self.waveform_panel.plot_waveform(self.current_waveform)
        self.summary_panel.update_summary(self.current_waveform)
        self.statusBar().showMessage("Waveform expanded successfully")

    def open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open RecipeScope Project", "", f"RecipeScope (*{DEFAULT_PROJECT_EXTENSION})"
        )
        if not path:
            return
        self.current_recipe = self.project_io.load_project(path)
        self.current_project_path = path
        self.recipe_table.set_steps(self.current_recipe.steps)
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

    def open_settings(self) -> None:
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_about(self) -> None:
        AboutDialog(self).exec()
