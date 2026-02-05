from unittest.mock import Mock, patch, call
from pgva import PGVATCPConfig, PGVA
from pgva.utils.logging import Logging
from pymodbus.client import ModbusTcpClient

#com_port="COM1", tcp_port=502, host="192.168.0.1", baudrate=115200, unit_id=1
class TestPGVA:

    @patch("pgva.pgva.PGVA._backend", spec=True)
    def test_constructor_with_ip(self, mock_modbus_client):

        pgva_config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1", port=502)
        pgva = PGVA(pgva_config)

        assert isinstance(pgva, PGVA)
