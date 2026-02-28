"""
PGVA interface Front end.

Unified driver front-end exposing standard PGVA control API for both ModbusSerial and ModbusTCP
 communication clients
"""

import logging

from .pgva_communication import PGVAModbusClient, PGVAModbusSerial, PGVAModbusTCP
from .pgva_config import PGVAConfig, PGVASerialConfig, PGVATCPConfig

logger = logging.getLogger(__name__)


class PGVA:
    """
    PGVA driver class.

    This is the main class that the user will interact with
    to control the PGVA-1 device.
    """

    _backend: PGVAModbusClient

    def __init__(self, config: PGVAConfig):
        """
        PGVA driver class constructor.

        Args:
            config (PGVAConfig): A ModbusTCP or ModbusSerial config
                    type to allow the driver to connect to the
                    correct communication interface

        Returns:
            None

        Raises:
            NotImplementedError: If a serial configuration is passed through PGVA.
            TypeError: If config is not a supported PGVAConfig type for this driver.
        """
        if isinstance(config, PGVAConfig):
            self._config = config
            match config:
                case PGVASerialConfig():
                    logger.error("""
                        Serial support for PGVA communication is currently experimental.
                        The serial connected can be tested explicitly by instantiating PGVAModbusSerial and passing in the communication backend explicitly.
                    """)
                    raise NotImplementedError("Serial communication is experimental and must be invoked directly")
                    self._backend = PGVAModbusSerial(config=self._config)
                    logger.debug("PGVA front-end initialised with serial backend")
                case PGVATCPConfig():
                    self._backend = PGVAModbusTCP(config=self._config)
                    logger.debug("PGVA front-end initialised with TCP backend")
        else:
            logger.error("Unsupported configuration type passed to PGVA: %s", type(config).__name__)
            raise TypeError("Error, configuration passed in is not supported by driver")

    def set_output_pressure(self, pressure: int) -> None:
        """
        Sets the output pressure to PGVA.

        Args:
            pressure (int): Pressure in mBar between -450 ... 450

        Returns:
            None
        """
        self._backend.set_output_pressure(pressure)

    def trigger_actuation_valve(self, actuation_time: int) -> None:
        """
        Opens the actuation valve for a certain amount of time.

        Args:
            actuation_time (int): Time in milliseconds

        Returns:
            None
        """
        self._backend.set_actuation_time(actuation_time=actuation_time)

    def set_pressure_chamber(self, pressure: int) -> None:
        """
        Sets the internal pressure chamber.

        Args:
            pressure (int): Range between 0 and 450 mBar

        Returns:
            None
        """
        self._backend.set_pressure_chamber(pressure)

    def set_vacuum_chamber(self, vacuum: int) -> None:
        """
        Sets the internal vacuum chamber.

        Args:
            vacuum (int): Range between -450 and 0 mBar

        Returns:
            None
        """
        self._backend.set_vacuum_chamber(vacuum)

    def get_pressure_chamber(self) -> int:
        """
        Returns the current reading of the pressure chamber in mBar.

        Args:
            None

        Returns:
            Pressure chamber pressure in mBar
        """
        return self._backend.get_pressure_chamber()

    def get_vacuum_chamber(self) -> int:
        """
        Returns the current reading of the vacuum chamber in mBar.

        Args:
            None

        Returns:
            Vacuum chamber pressure in mBar
        """
        return self._backend.get_vacuum_chamber()

    def get_output_pressure(self) -> int:
        """
        Returns the output port pressure in mBar.

        Args:
            None

        Returns:
            Positive or negative pressure in mBar
        """
        return self._backend.get_output_pressure()

    def get_internal_sensor_data(self) -> dict:
        """
        Returns all the internal sensor data in mBar.

        Args:
            None

        Returns:
            All current readings of internal sensors
        """
        return self._backend.get_internal_sensor_data()

    def toggle_pump(self, toggle: bool) -> None:
        """
        Enable / Disables the pump.

        Args:
            toggle (bool): 1 for on, 0 for off

        Returns:
            None
        """
        self._backend.toggle_pump(toggle)

    def get_status_word(self) -> dict:
        """
        Gets the status word from the PGVA.

        Args:
            None

        Returns:
           Dictionary of the status word
        """
        return self._backend.get_status_word()

    def get_warning_word(self) -> dict:
        """
        Gets the warning word from the PGVA-1.

        Args:
            None

        Returns:
            Dictionary of warning word
        """
        return self._backend.get_warning_word()

    def get_error_word(self) -> dict:
        """
        Gets the error word from the PGVA-1.

        Args:
            None

        Returns:
            Dictionary of error word
        """
        return self._backend.get_error_word()

    def get_modbus_error_word(self) -> dict:
        """
        Get the error word from the PGVA-1.

        Args:
            None

        Returns:
            Dictionary of modbus error word
        """
        return self._backend.get_modbus_error_word()

    def toggle_trigger(self, trigger: bool) -> None:
        """
        Toggles the trigger.

        Args:
            trigger (bool): bool value for on or off

        Returns:
            None
        """
        self._backend.toggle_manual_trigger(trigger)

    def print_driver_information(self) -> None:
        """
        Prints driver information to console.

        Args:
            None

        Returns:
            None
        """
        self._backend.print_driver_information()
