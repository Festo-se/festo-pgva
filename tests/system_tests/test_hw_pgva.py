"""
Hardware integration tests for the PGVA driver.

These tests require a live PGVA-1 device connected over TCP/IP.
They are skipped automatically when the ``PGVA_IP`` environment variable
is not set.

Run with::

    PGVA_IP=192.168.0.1 uv run pytest -m hardware -v
"""

import pytest

from pgva import PGVA, PGVATCPConfig


# ---------------------------------------------------------------------------
# Construction / connection
# ---------------------------------------------------------------------------


@pytest.mark.hardware
def test_instance_type(pgva_hw):
    """Fixture returns a proper PGVA instance."""
    assert isinstance(pgva_hw, PGVA)


@pytest.mark.hardware
def test_config_stored(pgva_hw):
    """Config passed at construction is accessible on the instance."""
    assert isinstance(pgva_hw._config, PGVATCPConfig)


# ---------------------------------------------------------------------------
# Read-only API — structure & type checks
# ---------------------------------------------------------------------------


@pytest.mark.hardware
def test_get_status_word_returns_dict_with_expected_keys(pgva_hw):
    result = pgva_hw.get_status_word()
    assert isinstance(result, dict)
    expected_keys = {
        "Status",
        "Pump",
        "Pressure",
        "Vacuum",
        "EEPROM",
        "TargetPressure",
        "Trigger",
        "OutputValveControl",
        "OutputValve",
    }
    assert expected_keys.issubset(result.keys())


@pytest.mark.hardware
def test_get_warning_word_returns_dict_with_expected_keys(pgva_hw):
    result = pgva_hw.get_warning_word()
    assert isinstance(result, dict)
    expected_keys = {
        "SupplyVoltage",
        "VacuumThreshold",
        "PressureThreshold",
        "TargetPressure",
        "VacuumChamber",
        "Pump",
        "ExternalSensor",
    }
    assert expected_keys.issubset(result.keys())


@pytest.mark.hardware
def test_get_error_word_returns_dict_with_expected_keys(pgva_hw):
    result = pgva_hw.get_error_word()
    assert isinstance(result, dict)
    expected_keys = {
        "PumpTimeout",
        "TimeoutPressure",
        "ModbusError",
        "LowVoltage",
        "HighVoltage",
        "TimeoutExternalSensor",
    }
    assert expected_keys.issubset(result.keys())


@pytest.mark.hardware
def test_get_modbus_error_word_returns_dict(pgva_hw):
    result = pgva_hw.get_modbus_error_word()
    assert isinstance(result, dict)
    assert "OutputActuationTime" in result


@pytest.mark.hardware
def test_get_internal_sensor_data_returns_dict_with_expected_keys(pgva_hw):
    result = pgva_hw.get_internal_sensor_data()
    assert isinstance(result, dict)
    assert "VacuumChamber" in result
    assert "PressureChamber" in result
    assert "OutputPressure" in result


@pytest.mark.hardware
def test_get_pressure_chamber_returns_int(pgva_hw):
    result = pgva_hw.get_pressure_chamber()
    assert isinstance(result, int)


@pytest.mark.hardware
def test_get_vacuum_chamber_returns_int(pgva_hw):
    result = pgva_hw.get_vacuum_chamber()
    assert isinstance(result, int)


@pytest.mark.hardware
def test_get_output_pressure_returns_int(pgva_hw):
    result = pgva_hw.get_output_pressure()
    assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Informational — no assertion, just verify no exception
# ---------------------------------------------------------------------------


@pytest.mark.hardware
def test_print_driver_information_does_not_raise(pgva_hw):
    pgva_hw.print_driver_information()


# ---------------------------------------------------------------------------
# Write API — safe values only
# ---------------------------------------------------------------------------

# @pytest.mark.hardware
# def test_toggle_pump_on_and_off(pgva_hw):
#     """Enable then disable the pump without asserting on sensor state."""
#     pgva_hw.toggle_pump(True)
#     pgva_hw.toggle_pump(False)


@pytest.mark.hardware
def test_set_output_pressure_zero(pgva_hw):
    """Zero pressure is always a safe write."""
    pgva_hw.set_output_pressure(0)


@pytest.mark.hardware
def test_set_output_pressure_max(pgva_hw):
    """Zero pressure is always a safe write."""
    pgva_hw.set_output_pressure(450)


@pytest.mark.hardware
def test_set_output_pressure_min(pgva_hw):
    """Zero pressure is always a safe write."""
    pgva_hw.set_output_pressure(-450)


@pytest.mark.hardware
def test_set_pressure_chamber_midrange(pgva_hw):
    """500 mBar is a safe mid-range value for the pressure chamber."""
    pgva_hw.set_pressure_chamber(500)


@pytest.mark.hardware
def test_set_vacuum_chamber_midrange(pgva_hw):
    """-500 mBar is a safe mid-range value for the vacuum chamber."""
    pgva_hw.set_vacuum_chamber(-500)
