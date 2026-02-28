"""Shared pytest fixtures for the festo-pgva test suite.

Fixtures
--------
pgva_tcp_mock
    A ``PGVA`` instance whose backend is fully replaced by a
    ``MagicMock``.  No hardware or network connection is required.
    Use this in all unit tests.

pgva_hw
    A real ``PGVA`` instance connected to a live device.  The test is
    automatically skipped when the ``PGVA_IP`` environment variable is
    not set.  Mark any test that uses this fixture with
    ``@pytest.mark.hardware``.
"""

from os import getenv
from unittest.mock import MagicMock

import pytest

from pgva import PGVA, PGVATCPConfig


# ---------------------------------------------------------------------------
# Mock fixture — no hardware required
# ---------------------------------------------------------------------------


@pytest.fixture()
def pgva_tcp_mock(mocker):
    """Return a PGVA instance with its backend replaced by a MagicMock.

    The mock backend is pre-configured with plausible return values for
    every ``get_*`` method so that tests can assert on them without
    worrying about Modbus communication.
    """
    # Prevent PGVAModbusTCP.__init__ from opening a real socket.
    mock_backend = MagicMock()
    mock_backend.version = [2, 0, 45]

    # Sensible default return values for all read methods.
    mock_backend.get_pressure_chamber.return_value = 500
    mock_backend.get_vacuum_chamber.return_value = -400
    mock_backend.get_output_pressure.return_value = 100
    mock_backend.get_internal_sensor_data.return_value = {
        "VacuumChamber": -400,
        "PressureChamber": 500,
        "OutputPressure": 100,
    }
    mock_backend.get_status_word.return_value = {
        "Status": "Idle",
        "Pump": "Pump is off",
        "Pressure": "Pressure in the tank is nominal",
        "Vacuum": "Vacuum in the tank is nominal",
        "EEPROM": "No EEPROM write pending",
        "TargetPressure": "Target pressure achieved",
        "Trigger": "Trigger is closed",
        "OutputValveControl": "Exhaust valve management disabled",
        "OutputValve": "Exhaust valve closed",
    }
    mock_backend.get_warning_word.return_value = {
        "SupplyVoltage": "Reset",
        "VacuumThreshold": "Reset",
        "PressureThreshold": "Reset",
        "TargetPressure": "Reset",
        "VacuumChamber": "Reset",
        "Pump": "Reset",
        "ExternalSensor": "Reset",
    }
    mock_backend.get_error_word.return_value = {
        "PumpTimeout": "Reset",
        "TimeoutPressure": "Reset",
        "ModbusError": "Reset",
        "LowVoltage": "Reset",
        "HighVoltage": "Reset",
        "TimeoutExternalSensor": "Reset",
    }
    mock_backend.get_modbus_error_word.return_value = {
        "OutputActuationTime": "Reset",
    }

    # Patch PGVAModbusTCP so the constructor never touches the network.
    mocker.patch(
        "pgva.pgva.PGVAModbusTCP",
        return_value=mock_backend,
    )

    config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1", port=502, unit_id=1)
    instance = PGVA(config=config)
    # Expose the mock so individual tests can inspect calls or change return values.
    instance._mock_backend = mock_backend
    return instance


# ---------------------------------------------------------------------------
# Hardware fixture — requires a live device
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def pgva_hw():
    """Return a PGVA instance connected to a live device.

    The test module is skipped entirely when ``PGVA_IP`` is not set in
    the environment.  Run hardware tests with::

        PGVA_IP=192.168.0.1 uv run pytest -m hardware
    """
    ip = getenv("PGVA_IP")
    if not ip:
        pytest.skip("PGVA_IP environment variable not set — skipping hardware tests")

    config = PGVATCPConfig(interface="tcp/ip", ip=ip, port=502, unit_id=1)
    return PGVA(config=config)
