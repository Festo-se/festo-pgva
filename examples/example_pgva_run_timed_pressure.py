"""Example script to run timed pressure on a PGVA instance."""

from os import getenv

from pgva import PGVA, PGVATCPConfig

ip = getenv("PGVA_IP", "192.168.0.1")

"""Create a PGVA instance with TCP/IP configuration."""
pgva_config = PGVATCPConfig(interface="tcp/ip", unit_id=1, ip=ip, port=502)
"""Initialize the PGVA instance."""
pgva = PGVA(config=pgva_config)

"""Run a timed pressure process."""
actuation_time_ms = 100
target_pressure_mbar = 100
pgva.set_output_pressure(target_pressure_mbar)
pgva.trigger_actuation_valve(actuation_time_ms)
print(f"Timed pressure set to {target_pressure_mbar} mbar for {actuation_time_ms} ms")
