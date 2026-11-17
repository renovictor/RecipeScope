from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from recipescope.models.recipe_step import RecipeStep


@dataclass(slots=True)
class Recipe:
    name: str = "Untitled Recipe"
    description: str = ""
    steps: list[RecipeStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recipe":
        steps = [RecipeStep.from_dict(row) for row in data.get("steps", [])]
        return cls(
            name=data.get("name", "Untitled Recipe"),
            description=data.get("description", ""),
            steps=steps,
        )
