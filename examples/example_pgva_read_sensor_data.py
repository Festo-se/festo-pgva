"""Example script to read the internal sensor values on a PGVA instance."""

from os import getenv

from pgva import PGVA, PGVATCPConfig

ip = getenv("PGVA_IP", "192.168.0.1")

"""Create a PGVA instance with TCP/IP configuration."""
pgva_config = PGVATCPConfig(interface="tcp/ip", unit_id=1, ip=ip, port=502)
"""Initialize the PGVA instance."""
pgva = PGVA(config=pgva_config)

"""Read and print all internal sensor data."""
data = pgva.get_internal_sensor_data()
print(f"Internal sensor data: {data}")
