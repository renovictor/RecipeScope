from recipescope.models import Recipe, RecipeStep
from recipescope.services.recipe_validator import RecipeValidator


def test_validator_success():
    recipe = Recipe(steps=[RecipeStep(step_name="A", duration=10, time_unit="ms", power=5, mode="CW")])
    result = RecipeValidator().validate(recipe)
    assert result.is_valid


def test_validator_detects_errors():
    recipe = Recipe(steps=[RecipeStep(step_name="", duration=0, time_unit="bad", power_unit="bad")])
    result = RecipeValidator().validate(recipe)
    assert not result.is_valid
    assert len(result.errors) >= 3
