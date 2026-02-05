from pgva import PGVATCPConfig, PGVA
import pytest

@pytest.fixture()
def create_pgva_tcp_instance():
    config = PGVATCPConfig(interface="tcp/ip", ip="192.168.0.1", port=502, unit_id=1)
    pgva_instance = PGVA(config)
    return pgva_instance

def test_instance(reate_pgva_tcp_instance):
    assert isinstance(create_pgva_tcp_instance, PGVA)

def test_config(create_pgva_tcp_instance):
    assert isinstance(create_pgva_tcp_instance._config, PGVATCPConfig)

