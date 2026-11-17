from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot

from recipescope.models import Recipe
from recipescope.services.recipe_engine import RecipeEngine


class WaveformWorker(QObject):
    finished = Signal(pd.DataFrame)
    failed = Signal(str)

    def __init__(self, recipe: Recipe) -> None:
        super().__init__()
        self.recipe = recipe
        self.engine = RecipeEngine()

    @Slot()
    def run(self) -> None:
        try:
            self.finished.emit(self.engine.expand_recipe(self.recipe))
        except Exception as exc:  # pragma: no cover
            self.failed.emit(str(exc))
