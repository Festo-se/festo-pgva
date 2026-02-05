"""
Front end PGVA interface
"""

from .pgva_communication import PGVAModbusClient, PGVAModbusSerial, PGVAModbusTCP
from .pgva_config import PGVAConfig, PGVASerialConfig, PGVATCPConfig
from .utils.logging import Logging


class PGVA:
    """
    PGVA driver class. This is the main class that the user will interact with
    to control the PGVA-1 device.
    """

    _backend: PGVAModbusClient

    def __init__(self, config: PGVAConfig):
        """
        Constructor\n
        Args:
            config (PGVAConfig): A ModbusTCP or ModbusSerial config
                    type to allow the driver to connect to the
                    correct communication interface
        \n
        Returns:
            None
        """

        if isinstance(config, PGVAConfig):
            self._config = config
            match config:
                case PGVASerialConfig():
                    Logging.logger.error("Serial support for PGVA communication is currently experimental.")
                    Logging.logger.error(
                        "The serial connected can be tested explicitly by instantiating PGVAModbusSerial and passing in the communication backend explicitly."
                    )
                    raise NotImplementedError("Serial communication is experimental and must be invoked directly")
                    self._backend = PGVAModbusSerial(config=self._config)
                case PGVATCPConfig():
                    self._backend = PGVAModbusTCP(config=self._config)
        else:
            raise TypeError("Error, configuration passed in is not supported by driver")

    def set_output_pressure(self, pressure: int) -> None:
        """
        Sets the output pressure to PGVA\n
        Args:
            pressure (int): Pressure in mBar between -450 ... 450\n
        Returns:
            None
        """
        self._backend.set_output_pressure(pressure)

    def trigger_actuation_valve(self, actuation_time: int) -> None:
        """
        Opens the actuation valve for a certain amount of time\n
        Args:
            actuation_time (int): Time in milliseconds\n
        Returns:
            None
        """
        self._backend.set_actuation_time(actuation_time=actuation_time)

    def set_pressure_chamber(self, pressure: int) -> None:
        """
        Sets the internal pressure chamber\n
        Args:
            pressure (int): Range between 0 and 450 mBar\n
        Returns:
            None
        """
        self._backend.set_pressure_chamber(pressure)

    def set_vacuum_chamber(self, vacuum: int) -> None:
        """
        Sets the internal vacuum chamber\n
        Args:
            vacuum (int): Range between -450 and 0 mBar\n
        Returns:
            None
        """
        self._backend.set_vacuum_chamber(vacuum)

    def get_pressure_chamber(self) -> int:
        """
        Returns the current reading of the pressure chamber in mBar\n
        Args:
            None\n
        Returns:
            Pressure chamber pressure in mBar
        """
        return self._backend.get_pressure_chamber()

    def get_vacuum_chamber(self) -> int:
        """
        Returns the current reading of the vacuum chamber in mBar\n
        Args:
            None\n
        Returns:
            Vacuum chamber pressure in mBar
        """
        return self._backend.get_vacuum_chamber()

    def get_output_pressure(self) -> int:
        """
        Returns the output port pressure in mBar\n
        Args:
            None\n
        Returns:
            Positive or negative pressure in mBar
        """
        return self._backend.get_output_pressure()

    def get_internal_sensor_data(self) -> dict:
        """
        Returns all the internal sensor data in mBar\n
        Args:
            None\n
        Returns:
            All current readings of internal sensors
        """
        return self._backend.get_internal_sensor_data()

    def toggle_pump(self, toggle: bool) -> None:
        """
        Enable / Disables the pump\n
        Args:
            toggle (bool): 1 for on, 0 for off\n
        Returns:
            None
        """
        self._backend.toggle_pump(toggle)

    def get_status_word(self) -> dict:
        """
        Gets the status word from the PGVA\n
        Args:
            None\n
        Returns:
           Dictionary of the status word
        """
        return self._backend.get_status_word()

    def get_warning_word(self) -> dict:
        """
        Gets the warning word from the PGVA-1\n
        Args:
            None\n
        Returns:
            Dictionary of warning word
        """
        return self._backend.get_warning_word()

    def get_error_word(self) -> dict:
        """
        Gets the error word from the PGVA-1\n
        Args:
            None\n
        Returns:
            Dictionary of error word
        """
        return self._backend.get_error_word()

    def get_modbus_error_word(self) -> dict:
        """
        Get the error word from the PGVA-1\n
        Args:
            None\n
        Returns:
            Dictionary of modbus error word
        """
        return self._backend.get_modbus_error_word()

    def toggle_trigger(self, trigger: bool) -> None:
        """
        Toggles the trigger\n
        Args:
            trigger (bool): bool value for on or off\n
        Returns:
            None
        """
        self._backend.toggle_manual_trigger(trigger)

    def print_driver_information(self) -> None:
        """
        Prints driver information to console\n
        Args:
            None\n
        Returns:
            None
        """
        self._backend.print_driver_information()
