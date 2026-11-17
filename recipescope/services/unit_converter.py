from __future__ import annotations


class UnitConverter:
    TIME_TO_SECONDS = {
        "ns": 1e-9,
        "us": 1e-6,
        "µs": 1e-6,
        "ms": 1e-3,
        "s": 1.0,
        "min": 60.0,
    }
    POWER_TO_WATTS = {"mW": 1e-3, "W": 1.0, "kW": 1e3}
    FREQ_TO_HZ = {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6}

    @classmethod
    def time_to_seconds(cls, value: float, unit: str) -> float:
        return float(value) * cls.TIME_TO_SECONDS[unit]

    @classmethod
    def seconds_to_time(cls, value: float, unit: str) -> float:
        return float(value) / cls.TIME_TO_SECONDS[unit]

    @classmethod
    def power_to_watts(cls, value: float, unit: str) -> float:
        return float(value) * cls.POWER_TO_WATTS[unit]

    @classmethod
    def watts_to_power(cls, value: float, unit: str) -> float:
        return float(value) / cls.POWER_TO_WATTS[unit]

    @classmethod
    def frequency_to_hz(cls, value: float, unit: str) -> float:
        return float(value) * cls.FREQ_TO_HZ[unit]
