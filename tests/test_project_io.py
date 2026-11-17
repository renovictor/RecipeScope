from pathlib import Path

from recipescope.models import Recipe, RecipeStep
from recipescope.services.project_io import ProjectIO


def test_project_save_load_roundtrip(tmp_path: Path):
    recipe = Recipe(name="R1", steps=[RecipeStep(step_name="S1", duration=1, time_unit="s", power=10, mode="CW")])
    path = tmp_path / "test.rscp.json"
    io = ProjectIO()
    io.save_project(recipe, path)
    loaded = io.load_project(path)
    assert loaded.name == "R1"
    assert loaded.steps[0].step_name == "S1"
