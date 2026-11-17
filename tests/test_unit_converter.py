from recipescope.services.unit_converter import UnitConverter


def test_time_conversion():
    assert UnitConverter.time_to_seconds(50, "ms") == 0.05
    assert UnitConverter.seconds_to_time(0.05, "ms") == 50


def test_power_conversion():
    assert UnitConverter.power_to_watts(1500, "mW") == 1.5
    assert UnitConverter.watts_to_power(2.0, "kW") == 0.002
