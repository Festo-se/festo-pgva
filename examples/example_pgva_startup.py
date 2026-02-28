"""Example script to start a PGVA instance with TCP/IP configuration."""

from os import getenv

from pgva import PGVA, PGVATCPConfig
from festo_python_logging import configure_logging

configure_logging(verbose=True, silence=["pymodbus.logging"])

ip = getenv("PGVA_IP", "192.168.0.1")

"""Create a PGVA instance with TCP/IP configuration."""
pgva_config = PGVATCPConfig(interface="tcp/ip", unit_id=1, ip=ip, port=502)
"""Initialize the PGVA instance."""
pgva = PGVA(config=pgva_config)
