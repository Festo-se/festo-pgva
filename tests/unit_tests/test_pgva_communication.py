"""
Unit tests for PGVAModbusClient backend — validation, conversion, and timeout.

These tests exercise the logic inside ``PGVAModbusClient`` (the ABC) via the
concrete ``PGVAModbusTCP`` subclass so that no actual Modbus/TCP connection is
opened.  All I/O is replaced by ``MagicMock`` objects.

Coverage areas
--------------
* ``_convert_twos_comp`` — parametrised positive / negative / boundary cases
* ``set_output_pressure`` — boundary enforcement (valid, below min, above max)
* ``set_pressure_chamber`` — boundary enforcement
* ``set_vacuum_chamber`` — boundary enforcement
* ``set_actuation_time`` — range enforcement
* ``toggle_manual_trigger`` — always raises NotImplementedError
* ``_validate_pump_enable`` — pump enabled / disabled / firmware 2.1.3 bypass
* ``_set_data`` — TimeoutError raised when device remains busy
"""

from unittest.mock import MagicMock

import pytest

from pgva.pgva_communication import PGVAModbusTCP
from pgva.pgva_config import PGVATCPConfig


# ---------------------------------------------------------------------------
# Shared fixture — PGVAModbusTCP instance with fully mocked pymodbus client
# ---------------------------------------------------------------------------


def _make_register_response(value: int) -> MagicMock:
    """Return a MagicMock whose .registers[0] equals *value*."""
    resp = MagicMock()
    resp.registers = [value]
    return resp


@pytest.fixture()
def tcp_backend(mocker):
    """``PGVAModbusTCP`` with its ``ModbusTcpClient`` replaced by a ``MagicMock``.

    After construction the ``instance.version`` attribute is forced to
    ``[2, 0, 45]`` so individual tests start from a known, deterministic state.
    The underlying mock client is accessible as ``instance._mock_client``.
    """
    mock_client = MagicMock()
    # read_input_registers is called 3 times by get_firmware_version during __init__.
    mock_client.read_input_registers.return_value = _make_register_response(0)
    mocker.patch(
        "pgva.pgva_communication.ModbusTcpClient",
        return_value=mock_client,
    )

    config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1", port=502, unit_id=1)
    backend = PGVAModbusTCP(config=config)

    # Override whatever version the mock returned during construction.
    backend.version = [2, 0, 45]
    backend._mock_client = mock_client
    return backend


# ---------------------------------------------------------------------------
# _convert_twos_comp
# ---------------------------------------------------------------------------


class TestConvertTwosComp:
    """``_convert_twos_comp(val, bits)`` converts raw unsigned register values."""

    @pytest.mark.parametrize(
        "val, bits, expected",
        [
            # --- Positive values (MSB clear) ---
            (0, 1, 0),  # zero, 1-bit
            (1, 2, 1),  # 01 in 2-bit — MSB is 0, stays positive
            (7, 4, 7),  # 0111 — MSB clear
            (127, 8, 127),  # max positive 8-bit signed
            (32767, 16, 32767),  # max positive 16-bit signed
            # --- Negative values (MSB set) ---
            (128, 8, -128),  # 1000 0000 → -128
            (200, 8, -56),  # 200 - 256 = -56
            (255, 8, -1),  # 1111 1111 → -1
            (32768, 16, -32768),  # 1000 0000 0000 0000 → -32768
            (65086, 16, -450),  # -450 encoded as unsigned 16-bit
            (65535, 16, -1),  # all-ones 16-bit → -1
        ],
    )
    def test_conversion(self, tcp_backend, val, bits, expected):
        assert tcp_backend._convert_twos_comp(val, bits) == expected


# ---------------------------------------------------------------------------
# set_output_pressure — validation
# ---------------------------------------------------------------------------


class TestSetOutputPressure:
    """Valid pressures are passed through; out-of-range values raise ValueError."""

    def test_valid_positive_pressure_accepted(self, tcp_backend):
        # Pre-condition: pump must appear enabled
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(1)
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_output_pressure(200)  # should not raise

    def test_valid_negative_pressure_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(1)
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_output_pressure(-200)

    def test_maximum_boundary_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(1)
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_output_pressure(450)

    def test_minimum_boundary_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(1)
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_output_pressure(-450)

    def test_above_maximum_raises_value_error(self, tcp_backend):
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(1)
        with pytest.raises(ValueError):
            tcp_backend.set_output_pressure(451)

    def test_below_minimum_raises_value_error(self, tcp_backend):
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(1)
        with pytest.raises(ValueError):
            tcp_backend.set_output_pressure(-451)


# ---------------------------------------------------------------------------
# set_pressure_chamber — validation
# ---------------------------------------------------------------------------


class TestSetPressureChamber:
    """Valid range 200–1000 mBar; outside raises ValueError."""

    def test_minimum_boundary_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_pressure_chamber(200)

    def test_maximum_boundary_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_pressure_chamber(1000)

    def test_midpoint_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_pressure_chamber(600)

    def test_below_minimum_raises_value_error(self, tcp_backend):
        with pytest.raises(ValueError):
            tcp_backend.set_pressure_chamber(199)

    def test_above_maximum_raises_value_error(self, tcp_backend):
        with pytest.raises(ValueError):
            tcp_backend.set_pressure_chamber(1001)


# ---------------------------------------------------------------------------
# set_vacuum_chamber — validation
# ---------------------------------------------------------------------------


class TestSetVacuumChamber:
    """Valid range -900–-200 mBar; outside raises ValueError."""

    def test_minimum_boundary_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_vacuum_chamber(-900)

    def test_maximum_boundary_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_vacuum_chamber(-200)

    def test_midpoint_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_vacuum_chamber(-500)

    def test_above_maximum_raises_value_error(self, tcp_backend):
        """Values less negative than -200 are outside the valid range."""
        with pytest.raises(ValueError):
            tcp_backend.set_vacuum_chamber(-199)

    def test_below_minimum_raises_value_error(self, tcp_backend):
        with pytest.raises(ValueError):
            tcp_backend.set_vacuum_chamber(-901)


# ---------------------------------------------------------------------------
# set_actuation_time — validation
# ---------------------------------------------------------------------------


class TestSetActuationTime:
    """Valid range 5–65534 ms; outside raises ValueError."""

    def test_minimum_boundary_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_actuation_time(5)

    def test_large_valid_value_accepted(self, tcp_backend):
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)
        tcp_backend.set_actuation_time(1000)

    def test_below_minimum_raises_value_error(self, tcp_backend):
        with pytest.raises(ValueError):
            tcp_backend.set_actuation_time(4)

    def test_at_upper_exclusive_boundary_raises_value_error(self, tcp_backend):
        """65535 is not in range(5, 65535), so it must be rejected."""
        with pytest.raises(ValueError):
            tcp_backend.set_actuation_time(65535)

    def test_zero_raises_value_error(self, tcp_backend):
        with pytest.raises(ValueError):
            tcp_backend.set_actuation_time(0)


# ---------------------------------------------------------------------------
# toggle_manual_trigger — always NotImplementedError
# ---------------------------------------------------------------------------


class TestToggleManualTrigger:
    def test_true_raises_not_implemented(self, tcp_backend):
        with pytest.raises(NotImplementedError):
            tcp_backend.toggle_manual_trigger(True)

    def test_false_raises_not_implemented(self, tcp_backend):
        with pytest.raises(NotImplementedError):
            tcp_backend.toggle_manual_trigger(False)


# ---------------------------------------------------------------------------
# _validate_pump_enable
# ---------------------------------------------------------------------------


class TestValidatePumpEnable:
    def test_returns_true_when_pump_enabled(self, tcp_backend):
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(1)
        assert tcp_backend._validate_pump_enable() is True

    def test_returns_false_when_pump_disabled(self, tcp_backend):
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(0)
        assert tcp_backend._validate_pump_enable() is False

    def test_returns_true_for_firmware_2_1_3_regardless_of_register(self, tcp_backend):
        """Firmware 2.1.3 does not support pump enable — always returns True."""
        tcp_backend.version = [2, 1, 3]
        # Even if holding register says 0, the bypass should fire.
        tcp_backend._mock_client.read_holding_registers.return_value = _make_register_response(0)
        assert tcp_backend._validate_pump_enable() is True


# ---------------------------------------------------------------------------
# _set_data — TimeoutError when device remains busy
# ---------------------------------------------------------------------------


class TestSetDataTimeout:
    def test_raises_timeout_error_when_device_stays_busy(self, tcp_backend):
        """If the status word busy bit never clears, TimeoutError must be raised."""
        # write_register succeeds silently.
        tcp_backend._mock_client.write_register.return_value = MagicMock()
        # read_input_registers always returns status=1 (busy bit set).
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(1)

        from pgva.registers import _PGVARegisters as commands

        with pytest.raises(TimeoutError):
            tcp_backend._set_data(commands.OUTPUT_PRESSURE_MBAR, 100, timeout=0.05)

    def test_completes_without_error_when_device_is_not_busy(self, tcp_backend):
        """If the initial status read shows not-busy, _set_data returns normally."""
        tcp_backend._mock_client.write_register.return_value = MagicMock()
        # First read_input_registers (status poll) returns 0 — not busy.
        tcp_backend._mock_client.read_input_registers.return_value = _make_register_response(0)

        from pgva.registers import _PGVARegisters as commands

        # Should complete without exception.
        tcp_backend._set_data(commands.OUTPUT_PRESSURE_MBAR, 100, timeout=1.0)
