from __future__ import annotations

import json
from pathlib import Path

from recipescope.models import Recipe
from version import VERSION


class ProjectIO:
    def save_project(self, recipe: Recipe, file_path: str | Path) -> None:
        payload = {
            "schema_version": 1,
            "app_version": VERSION,
            "recipe": recipe.to_dict(),
        }
        target = Path(file_path)
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_project(self, file_path: str | Path) -> Recipe:
        source = Path(file_path)
        payload = json.loads(source.read_text(encoding="utf-8"))
        return Recipe.from_dict(payload["recipe"])
