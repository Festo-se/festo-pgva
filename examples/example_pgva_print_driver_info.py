"""Example script to start a PGVA instance with TCP/IP configuration."""

# TODO: Use env variable for IP here and all examples
from os import getenv

from pgva import PGVA, PGVATCPConfig

ip = getenv("PGVA_IP", "192.168.0.1")

"""Create a PGVA instance with TCP/IP configuration."""
pgva_config = PGVATCPConfig(interface="tcp/ip", unit_id=1, ip=ip, port=502)
"""Initialize the PGVA instance."""
pgva = PGVA(config=pgva_config)

"""Print driver information."""
pgva.print_driver_information()
