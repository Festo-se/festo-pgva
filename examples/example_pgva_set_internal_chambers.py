"""Example script to set internal pressure and vacuum chambers on a PGVA instance."""

from os import getenv

from pgva import PGVA, PGVATCPConfig
from festo_python_logging import configure_logging

configure_logging(verbose=True, silence=["pymodbus.logging"])

ip = getenv("PGVA_IP", "192.168.0.1")

"""Create a PGVA instance with TCP/IP configuration."""
pgva_config = PGVATCPConfig(interface="tcp/ip", unit_id=1, ip=ip, port=502)
"""Initialize the PGVA instance."""
pgva = PGVA(config=pgva_config)

"""Set the internal pressure chamber to a specified value (e.g., 100 mbar)."""
internal_pressure_mbar = 200
pgva.set_pressure_chamber(internal_pressure_mbar)

"""Set the internal vacuum chamber to a specified value (e.g., -100 mbar)."""
internal_vacuum_mbar = -200
pgva.set_vacuum_chamber(internal_vacuum_mbar)
