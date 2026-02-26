"""Unit tests for PGVA public API — delegation to backend.

Every public method on ``PGVA`` is a thin wrapper that forwards to
``self._backend``.  These tests verify:

* the correct backend method is called,
* the correct arguments are forwarded, and
* the return value from the backend is passed back to the caller.

All tests use the ``pgva_tcp_mock`` fixture (no hardware required).
"""



# ---------------------------------------------------------------------------
# Setters — verify correct delegation and argument forwarding
# ---------------------------------------------------------------------------


class TestSetOutputPressure:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.set_output_pressure(200)
        pgva_tcp_mock._mock_backend.set_output_pressure.assert_called_once_with(200)

    def test_negative_pressure_forwarded(self, pgva_tcp_mock):
        pgva_tcp_mock.set_output_pressure(-150)
        pgva_tcp_mock._mock_backend.set_output_pressure.assert_called_once_with(-150)

    def test_returns_none(self, pgva_tcp_mock):
        result = pgva_tcp_mock.set_output_pressure(0)
        assert result is None


class TestTriggerActuationValve:
    def test_delegates_to_set_actuation_time(self, pgva_tcp_mock):
        pgva_tcp_mock.trigger_actuation_valve(500)
        pgva_tcp_mock._mock_backend.set_actuation_time.assert_called_once_with(actuation_time=500)

    def test_returns_none(self, pgva_tcp_mock):
        result = pgva_tcp_mock.trigger_actuation_valve(100)
        assert result is None


class TestSetPressureChamber:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.set_pressure_chamber(300)
        pgva_tcp_mock._mock_backend.set_pressure_chamber.assert_called_once_with(300)

    def test_returns_none(self, pgva_tcp_mock):
        result = pgva_tcp_mock.set_pressure_chamber(300)
        assert result is None


class TestSetVacuumChamber:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.set_vacuum_chamber(-300)
        pgva_tcp_mock._mock_backend.set_vacuum_chamber.assert_called_once_with(-300)

    def test_returns_none(self, pgva_tcp_mock):
        result = pgva_tcp_mock.set_vacuum_chamber(-300)
        assert result is None


# ---------------------------------------------------------------------------
# Getters — verify delegation and return value pass-through
# ---------------------------------------------------------------------------


class TestGetPressureChamber:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_pressure_chamber()
        pgva_tcp_mock._mock_backend.get_pressure_chamber.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_pressure_chamber()
        assert result == pgva_tcp_mock._mock_backend.get_pressure_chamber.return_value


class TestGetVacuumChamber:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_vacuum_chamber()
        pgva_tcp_mock._mock_backend.get_vacuum_chamber.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_vacuum_chamber()
        assert result == pgva_tcp_mock._mock_backend.get_vacuum_chamber.return_value


class TestGetOutputPressure:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_output_pressure()
        pgva_tcp_mock._mock_backend.get_output_pressure.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_output_pressure()
        assert result == pgva_tcp_mock._mock_backend.get_output_pressure.return_value


class TestGetInternalSensorData:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_internal_sensor_data()
        pgva_tcp_mock._mock_backend.get_internal_sensor_data.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_internal_sensor_data()
        assert result == pgva_tcp_mock._mock_backend.get_internal_sensor_data.return_value

    def test_return_type_is_dict(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_internal_sensor_data()
        assert isinstance(result, dict)


class TestGetStatusWord:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_status_word()
        pgva_tcp_mock._mock_backend.get_status_word.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_status_word()
        assert result == pgva_tcp_mock._mock_backend.get_status_word.return_value


class TestGetWarningWord:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_warning_word()
        pgva_tcp_mock._mock_backend.get_warning_word.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_warning_word()
        assert result == pgva_tcp_mock._mock_backend.get_warning_word.return_value


class TestGetErrorWord:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_error_word()
        pgva_tcp_mock._mock_backend.get_error_word.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_error_word()
        assert result == pgva_tcp_mock._mock_backend.get_error_word.return_value


class TestGetModbusErrorWord:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.get_modbus_error_word()
        pgva_tcp_mock._mock_backend.get_modbus_error_word.assert_called_once_with()

    def test_returns_backend_value(self, pgva_tcp_mock):
        result = pgva_tcp_mock.get_modbus_error_word()
        assert result == pgva_tcp_mock._mock_backend.get_modbus_error_word.return_value


# ---------------------------------------------------------------------------
# Toggle methods
# ---------------------------------------------------------------------------


class TestTogglePump:
    def test_enable_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.toggle_pump(True)
        pgva_tcp_mock._mock_backend.toggle_pump.assert_called_once_with(True)

    def test_disable_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.toggle_pump(False)
        pgva_tcp_mock._mock_backend.toggle_pump.assert_called_once_with(False)

    def test_returns_none(self, pgva_tcp_mock):
        result = pgva_tcp_mock.toggle_pump(True)
        assert result is None


class TestToggleTrigger:
    """toggle_trigger delegates to the backend's toggle_manual_trigger (note name difference)."""

    def test_enable_delegates_to_toggle_manual_trigger(self, pgva_tcp_mock):
        pgva_tcp_mock.toggle_trigger(True)
        pgva_tcp_mock._mock_backend.toggle_manual_trigger.assert_called_once_with(True)

    def test_disable_delegates_to_toggle_manual_trigger(self, pgva_tcp_mock):
        pgva_tcp_mock.toggle_trigger(False)
        pgva_tcp_mock._mock_backend.toggle_manual_trigger.assert_called_once_with(False)

    def test_returns_none(self, pgva_tcp_mock):
        result = pgva_tcp_mock.toggle_trigger(True)
        assert result is None


# ---------------------------------------------------------------------------
# Informational methods
# ---------------------------------------------------------------------------


class TestPrintDriverInformation:
    def test_delegates_to_backend(self, pgva_tcp_mock):
        pgva_tcp_mock.print_driver_information()
        pgva_tcp_mock._mock_backend.print_driver_information.assert_called_once_with()

    def test_returns_none(self, pgva_tcp_mock):
        result = pgva_tcp_mock.print_driver_information()
        assert result is None
