from unittest.mock import MagicMock, patch

from pgva import PGVATCPConfig, PGVA


class TestPGVA:
    @patch("pgva.pgva.PGVAModbusTCP")
    def test_constructor_with_ip(self, mock_tcp_class):
        mock_tcp_class.return_value = MagicMock()

        pgva_config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1", port=502)
        pgva = PGVA(pgva_config)

        assert isinstance(pgva, PGVA)
