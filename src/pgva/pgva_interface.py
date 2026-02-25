"""
PGVA Interface class.

Abstract interface description for exportation to CoDeSys libraries and other systems for consistent integration
"""

from abc import ABC, abstractmethod


class PGVAInterface(ABC):
    """Interface class for PGVA that needs to be implemented by the user."""

    @abstractmethod
    def __init__(self, config):
        """Abstract function for constructor of the driver class."""
        pass

    @abstractmethod
    def set_output_pressure(self, pressure: int):
        """Abstract function for setting output pressure."""
        pass

    @abstractmethod
    def trigger_actuation_valve(self, actuation_time: int):
        """Abstract function for running the actuation valve."""
        pass

    @abstractmethod
    def set_pressure_chamber(self, pressure: int):
        """Abstract function for setting internal pressure chamber."""
        pass

    @abstractmethod
    def set_vacuum_chamber(self, vacuum: int):
        """
        Sets the internal vacuum chamber.

        Args:
            vacuum: mBar
        """
        pass

    @abstractmethod
    def get_pressure_chamber(self):
        """
        Returns the current reading of the pressure chamber in mBar.

        Returns:
            Chamber pressure
        """
        pass

    @abstractmethod
    def get_vacuum_chamber(self):
        """
        Returns the current reading of the vacuum chamber in mBar.

        Returns:
            Vacuum pressure
        """
        pass

    @abstractmethod
    def get_output_pressure(self):
        """
        Returns the output port pressure in mBar.

        Returns:
            Output Pressure
        """
        pass

    @abstractmethod
    def get_internal_sensor_data(self):
        """
        Returns all the internal sensor data in mBar.

        Returns:
            Dictionary: All current readings of internal sensors
        """
        pass

    @abstractmethod
    def toggle_pump(self, toggle: bool):
        """
        Enable / Disables the pump.

        Args:
            toggle: 1 for on, 0 for off
        """
        pass

    @abstractmethod
    def get_status_word(self):
        """
        Gets the status word from the PGVA.

        Returns:
            Status word: Dictionary of status
        """
        pass

    @abstractmethod
    def get_warning_word(self):
        """
        Gets the warning word from the PGVA-1.

        Returns:
            Warning word: Dictionary of warning word
        """
        pass

    @abstractmethod
    def get_error_word(self):
        """
        Gets the error word from the PGVA-1.

        Returns:
            Error word: Dictionary of error word
        """
        pass

    @abstractmethod
    def get_modbus_error_word(self):
        """
        Get the error word from the PGVA-1.

        Returns:
            Modbus error word: Dictionary of modbus error word
        """
        pass

    @abstractmethod
    def toggle_trigger(self, trigger: bool):
        """
        Toggles the trigger.

        Args:
            trigger: boolean value for on or off
        """
        pass
