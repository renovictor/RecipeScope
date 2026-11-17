from __future__ import annotations

from recipescope.constants import MODES, POWER_UNITS, TIME_UNITS
from recipescope.models import Recipe, ValidationResult


class RecipeValidator:
    def validate(self, recipe: Recipe) -> ValidationResult:
        result = ValidationResult()
        if not recipe.steps:
            result.add_error("Recipe must contain at least one step.")
            return result

        for idx, step in enumerate(recipe.steps, start=1):
            if not step.enabled:
                continue
            if not step.step_name.strip():
                result.add_error("Step name is required.", idx)
            if step.duration <= 0:
                result.add_error("Duration must be greater than zero.", idx)
            if step.time_unit not in TIME_UNITS:
                result.add_error(f"Unsupported time unit: {step.time_unit}", idx)
            if step.power_unit not in POWER_UNITS:
                result.add_error(f"Unsupported power unit: {step.power_unit}", idx)
            if step.mode not in MODES:
                result.add_error(f"Unsupported mode: {step.mode}", idx)
            if step.repeat_count < 1:
                result.add_error("Repeat count must be >= 1.", idx)

            if step.mode == "Idle" and step.power != 0:
                result.add_warning("Idle step has non-zero power.", idx)

            if step.mode == "Pulse":
                if step.pulse_frequency <= 0:
                    result.add_error("Pulse frequency must be greater than zero.", idx)
                if not 0 < step.duty_cycle_percent <= 100:
                    result.add_error("Duty cycle must be in (0, 100].", idx)

            if step.mode in ("Ramp Up", "Ramp Down"):
                if step.start_power == step.end_power:
                    result.add_warning(
                        "Ramp step start and end power are identical.", idx
                    )

        return result
