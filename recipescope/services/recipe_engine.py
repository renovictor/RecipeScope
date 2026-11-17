from __future__ import annotations

import math

import pandas as pd

from recipescope.models import Recipe, RecipeStep
from recipescope.services.unit_converter import UnitConverter

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None


class RecipeEngine:
    def expand_recipe(self, recipe: Recipe) -> pd.DataFrame:
        expanded: list[dict] = []
        current_time = 0.0
        i = 0
        while i < len(recipe.steps):
            step = recipe.steps[i]
            if not step.enabled:
                i += 1
                continue

            if step.cycle_group:
                group_steps = self._collect_group_steps(recipe.steps, i, step.cycle_group)
                repeats = max(1, step.repeat_count)
                for cycle in range(1, repeats + 1):
                    for row in group_steps:
                        current_time = self._append_step_segments(
                            expanded, row, current_time, cycle
                        )
                i += len(group_steps)
                continue

            current_time = self._append_step_segments(expanded, step, current_time, 1)
            i += 1

        return pd.DataFrame(expanded)

    @staticmethod
    def _collect_group_steps(steps: list[RecipeStep], start: int, group: str) -> list[RecipeStep]:
        out = []
        idx = start
        while idx < len(steps) and steps[idx].cycle_group == group:
            if steps[idx].enabled:
                out.append(steps[idx])
            idx += 1
        return out

    def _append_step_segments(
        self, rows: list[dict], step: RecipeStep, start_s: float, cycle_index: int
    ) -> float:
        duration_s = UnitConverter.time_to_seconds(step.duration, step.time_unit)
        end_s = start_s + duration_s

        if step.mode == "Idle":
            rows.extend(
                [
                    self._row(step, start_s, start_s, 0.0, cycle_index),
                    self._row(step, end_s, duration_s, 0.0, cycle_index),
                ]
            )
        elif step.mode == "CW":
            p_w = UnitConverter.power_to_watts(step.power, step.power_unit)
            rows.extend(
                [
                    self._row(step, start_s, start_s, p_w, cycle_index),
                    self._row(step, end_s, duration_s, p_w, cycle_index),
                ]
            )
        elif step.mode == "Pulse":
            self._append_pulse_rows(rows, step, start_s, duration_s, cycle_index)
        elif step.mode in ("Ramp Up", "Ramp Down"):
            p0 = UnitConverter.power_to_watts(step.start_power, step.power_unit)
            p1 = UnitConverter.power_to_watts(step.end_power, step.power_unit)
            rows.extend(
                [
                    self._row(step, start_s, start_s, p0, cycle_index),
                    self._row(step, end_s, duration_s, p1, cycle_index),
                ]
            )
        else:
            p_w = UnitConverter.power_to_watts(step.power, step.power_unit)
            rows.extend(
                [
                    self._row(step, start_s, start_s, p_w, cycle_index),
                    self._row(step, end_s, duration_s, p_w, cycle_index),
                ]
            )
        return end_s

    def _append_pulse_rows(
        self, rows: list[dict], step: RecipeStep, start_s: float, duration_s: float, cycle_index: int
    ) -> None:
        freq_hz = UnitConverter.frequency_to_hz(step.pulse_frequency, step.frequency_unit)
        period = 1.0 / freq_hz
        duty = step.duty_cycle_percent / 100.0
        high_w = UnitConverter.power_to_watts(
            step.high_power if step.high_power else step.power, step.power_unit
        )
        low_w = UnitConverter.power_to_watts(step.low_power, step.power_unit)
        if period <= 0:
            period = duration_s
        count = max(1, int(math.ceil(duration_s / period)))

        if np is not None:
            pulse_starts = np.arange(count, dtype=float) * period
            for offset in pulse_starts.tolist():
                t0 = start_s + offset
                if t0 >= start_s + duration_s:
                    break
                t1 = min(t0 + period * duty, start_s + duration_s)
                t2 = min(t0 + period, start_s + duration_s)
                rows.append(self._row(step, t0, t0 - start_s, high_w, cycle_index))
                rows.append(self._row(step, t1, t1 - start_s, low_w, cycle_index))
                rows.append(self._row(step, t2, t2 - start_s, low_w, cycle_index))
            return

        for i in range(count):
            t0 = start_s + i * period
            if t0 >= start_s + duration_s:
                break
            t1 = min(t0 + period * duty, start_s + duration_s)
            t2 = min(t0 + period, start_s + duration_s)
            rows.append(self._row(step, t0, t0 - start_s, high_w, cycle_index))
            rows.append(self._row(step, t1, t1 - start_s, low_w, cycle_index))
            rows.append(self._row(step, t2, t2 - start_s, low_w, cycle_index))

    @staticmethod
    def _row(step: RecipeStep, time_s: float, elapsed_s: float, power_w: float, cycle_index: int) -> dict:
        return {
            "step_name": step.step_name,
            "cycle_group": step.cycle_group,
            "cycle_index": cycle_index,
            "mode": step.mode,
            "time_s": float(time_s),
            "elapsed_in_step_s": float(elapsed_s),
            "power_w": float(power_w),
            "color": step.color,
            "notes": step.notes,
        }
