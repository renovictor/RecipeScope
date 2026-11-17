from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class RecipeStep:
    enabled: bool = True
    step_name: str = ""
    cycle_group: str = ""
    cycle_index: int = 1
    repeat_count: int = 1
    start: float = 0.0
    end: float = 0.0
    duration: float = 0.0
    time_unit: str = "ms"
    power: float = 0.0
    power_unit: str = "W"
    mode: str = "CW"
    color: str = "#1f77b4"
    notes: str = ""
    pulse_frequency: float = 1000.0
    frequency_unit: str = "Hz"
    duty_cycle_percent: float = 50.0
    high_power: float = 0.0
    low_power: float = 0.0
    start_power: float = 0.0
    end_power: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecipeStep":
        defaults = cls().to_dict()
        defaults.update(data)
        return cls(**defaults)
