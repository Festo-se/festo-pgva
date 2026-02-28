"""Unit tests for PGVA constructor and configuration dataclasses."""

import pytest

from pgva import PGVA, PGVATCPConfig, PGVASerialConfig


class TestPGVATCPConfig:
    """Tests for PGVATCPConfig dataclass defaults and field storage."""

    def test_required_fields_stored(self):
        config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1")
        assert config.ip == "192.168.0.1"
        assert config.interface == "tcp/ip"

    def test_default_port(self):
        config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1")
        assert config.port == 502

    def test_default_unit_id(self):
        config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1")
        assert config.unit_id == 1

    def test_custom_port(self):
        config = PGVATCPConfig(interface="tcp/ip", ip="10.0.0.5", port=5020)
        assert config.port == 5020

    def test_custom_unit_id(self):
        config = PGVATCPConfig(interface="tcp/ip", ip="10.0.0.5", unit_id=3)
        assert config.unit_id == 3


class TestPGVASerialConfig:
    """Tests for PGVASerialConfig dataclass field storage."""

    def test_required_fields_stored(self):
        config = PGVASerialConfig(interface="serial", com_port="COM3", baudrate=115200)
        assert config.com_port == "COM3"
        assert config.baudrate == 115200
        assert config.interface == "serial"

    def test_default_unit_id(self):
        config = PGVASerialConfig(interface="serial", com_port="/dev/ttyUSB0", baudrate=9600)
        assert config.unit_id == 1


class TestPGVAConstructor:
    """Tests for PGVA.__init__ error handling and backend selection."""

    def test_raises_type_error_for_non_config(self):
        with pytest.raises(TypeError):
            PGVA(config="not-a-config")

    def test_raises_type_error_for_none(self):
        with pytest.raises(TypeError):
            PGVA(config=None)

    def test_raises_not_implemented_for_serial_config(self):
        config = PGVASerialConfig(interface="serial", com_port="COM1", baudrate=115200)
        with pytest.raises(NotImplementedError):
            PGVA(config=config)

    def test_tcp_config_creates_instance(self, mocker):
        mocker.patch("pgva.pgva.PGVAModbusTCP")
        config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1")
        pgva = PGVA(config=config)
        assert isinstance(pgva, PGVA)

    def test_tcp_config_stored_on_instance(self, mocker):
        mocker.patch("pgva.pgva.PGVAModbusTCP")
        config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1")
        pgva = PGVA(config=config)
        assert pgva._config is config

    def test_tcp_backend_is_initialised(self, mocker):
        mock_tcp = mocker.patch("pgva.pgva.PGVAModbusTCP")
        config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1")
        PGVA(config=config)
        mock_tcp.assert_called_once_with(config=config)
