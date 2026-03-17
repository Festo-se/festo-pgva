"""Example script to set output vacuum on a PGVA instance."""

from os import getenv

from pgva import PGVA, PGVATCPConfig

try:
    from festo_python_logging import configure_logging

    configure_logging(verbose=True, silence=["pymodbus.logging"])
except Exception:
    import logging

    logging.basicConfig(
        level=logging.INFO,  # Set minimum level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("pgva")
    logger.warning("Festo Logger not in current working environment. Falling back to default")

ip = getenv("PGVA_IP", "192.168.0.1")

"""Create a PGVA instance with TCP/IP configuration."""
pgva_config = PGVATCPConfig(interface="tcp/ip", unit_id=1, ip=ip, port=502)
"""Initialize the PGVA instance."""
pgva = PGVA(config=pgva_config)

"""Set the output pressure to a specified value (e.g., 100 mbar)."""
output_vacuum_mbar = -100
pgva.set_output_pressure(output_vacuum_mbar)

"""Optionally, read back the output pressure to verify."""
output_vacuum_mbar_reading = pgva.get_output_pressure()
print(f"Output Vacuum set to: {output_vacuum_mbar_reading} mbar")
