import pytest

from recipescope.models import Recipe, RecipeStep
from recipescope.services.recipe_engine import RecipeEngine


def test_cycle_group_repeat_expansion():
    recipe = Recipe(
        steps=[
            RecipeStep(
                step_name="Depo",
                cycle_group="Main",
                repeat_count=2,
                duration=50,
                time_unit="ms",
                power=15,
                mode="CW",
            ),
            RecipeStep(
                step_name="Idle",
                cycle_group="Main",
                duration=150,
                time_unit="ms",
                power=0,
                mode="Idle",
            ),
        ]
    )
    df = RecipeEngine().expand_recipe(recipe)
    assert not df.empty
    assert set(df["cycle_index"].unique()) == {1, 2}
    assert pytest.approx(df["time_s"].max(), rel=1e-5) == 0.4
