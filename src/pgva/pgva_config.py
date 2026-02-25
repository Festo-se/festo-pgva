"""
Wrapper for the configurations of the PGVA communication backend.

This holds all the different PGVA-1 configurations for different backends
"""

from dataclasses import dataclass


@dataclass(kw_only=True)
class PGVAConfig:
    """
    Generic class PGVA-1 dataclass for initalization.

    Attributes:
        interface (str): Interface type. Ex: 'tcp/ip', 'serial', 'codes
        unit_id (int): Modbus unit ID of the PGVA-1 device
    """

    interface: str
    unit_id: int = 1


@dataclass(kw_only=True)
class PGVATCPConfig(PGVAConfig):
    """
    Class for PGVA-1 configuration class for ModbusTCP connection.

    Attributes:
        ip (str): IP address of PGVA in string form. Ex: '192.168.0.1'
        port (int): Default to 502, port of connunication for the PGVA-1
    """

    ip: str
    port: int = 502


@dataclass(kw_only=True)
class PGVASerialConfig(PGVAConfig):
    """
    Class PGVA-1 configuration for serial connection.

    Attributes:
        com_port (str): COM port of the serial connection. Ex: 'COM3' or '/dev/ttyUSB0'
        baudrate (int): Baudrate of the serial connection. Ex: 9600, 19200, 115200
    """

    com_port: str
    baudrate: int
