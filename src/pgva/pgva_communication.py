"""
PGVA-1 communication backend module.

PGVA driver communication backend implementation.
PGVA driver can use two different modes of communication to control the device, ModbusSerial and ModbusTCP.
These are implemented here.
"""

import socket
from abc import ABC, abstractmethod

from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from pymodbus.exceptions import ModbusException

import pgva.utils.constants as consts
from pgva.registers import _PGVARegisters as commands
from pgva.utils.logging import Logging

from .pgva_config import PGVASerialConfig, PGVATCPConfig, PGVAConfig


class PGVAModbusClient(ABC):
    """Modbus Client Class."""

    client: ModbusTcpClient | ModbusSerialClient
    version: list
    _pgva_error: dict
    _modbus_error: dict
    _warning: dict
    _status: dict

    @abstractmethod
    def __init__(self, config):
        """Base abstract class init, ModbusTCP and ModbusSerial will have their own implemenation."""
        self._config = config

    def get_firmware_version(self) -> list:
        """Gets the current firmware version located on the PGVA.

        Args:
            None

        Returns:
            List of the version
        """
        self.version = []
        if len(self.version) < 3:
            self.version.append(self._get_data(commands.FIRMWARE_VERSION))
            self.version.append(self._get_data(commands.FIRMWARE_SUBVERSION))
            self.version.append(self._get_data(commands.FIRMWARE_BUILD))
            Logging.logger.debug("Firmware version retrieved: %s", self.version)
            return self.version
        return [0, 0, 0]

    def _get_data(self, register):
        """
        Method used to access data from a register.

        Args:
            register: Register address for data access

        Returns:
            value: Value from register
        """
        data = 0
        Logging.logger.debug("Reading input register: %s", str(register))
        try:
            data = self.client.read_input_registers(
                address=int(register.value),
                count=1,
            )
            return data.registers[0]
        except ModbusException as modbus_pdu_exception:
            Logging.logger.error("Error while reading : %s", str(modbus_pdu_exception))
            return None
        except TypeError as type_err:
            Logging.logger.error("Error while reading: %s", str(type_err))
            return None

    def _get_data_holding(self, register):
        """Method used to read the holding registers."""
        data = 0
        Logging.logger.debug("Reading holding register: %s", str(register))
        try:
            data = self.client.read_holding_registers(
                address=int(register.value),
                count=1,
            )
            return data.registers[0]
        except ModbusException as modbus_pdu_exception:
            Logging.logger.error("Error while reading holding: %s", str(modbus_pdu_exception))
            return None
        except TypeError as type_err:
            Logging.logger.error("Error while reading holding: %s", str(type_err))
            return None

    def _set_data(self, register, val):
        """
        Method used to write to registers.

        Args:
            register: Register address for accessing
            val: Value to be writted to register
        """
        status = object
        Logging.logger.debug("Writing register %s, value: %s", str(register), str(val))
        try:
            if val < 0:
                val = val + 2**16
            self.client.write_register(
                address=int(register.value),
                value=val,
            )
            status = self.client.read_input_registers(
                address=int(commands.STATUS_WORD.value),
                count=1,
            )
            while (status.registers[0] & 1) == 1:
                status = self.client.read_input_registers(
                    address=int(commands.STATUS_WORD.value),
                    count=1,
                )
        except ModbusException as modbus_pdu_exception:
            Logging.logger.error("Modbus Exception Error : %s", str(modbus_pdu_exception))
        except TypeError as type_err:
            Logging.logger.error("Type error while writing data: %s", str(type_err))
            # calibration procedure for setting exact levels of P&V

    def set_output_pressure(self, pressure: int) -> None:
        """
        Sets the output pressure for the PGVA.

        Args:
            pressure (int): Any range between -450 ... 450

        Returns:
            None

        Raises:
            ValueError: If pressure is outside the supported output pressure range.
        """
        if self._validate_pump_enable():
            if consts.MINIMUM_OUTPUT_PRESSURE_MBAR <= pressure <= consts.MAXIMUM_OUTPUT_PRESSURE_MBAR:
                Logging.logger.info("Setting output pressure to %s mBar", pressure)
                self._set_data(commands.OUTPUT_PRESSURE_MBAR, pressure)
            else:
                Logging.logger.error("Input pressure outside of working range: %s", str(pressure))
                raise ValueError("Input pressure outside of working range")

    def set_actuation_time(self, actuation_time: int) -> None:
        """
        Sets the valve actuation time which is then immediately executed.

        Args:
            actuation_time (int): Time in ms for valve to be open

        Returns:
            None

        Raises:
            ValueError: If actuation_time is outside the valid range of 5 to 65535 ms.
        """
        if actuation_time in range(5, 65535):
            Logging.logger.info("Triggering actuation valve for %s ms", actuation_time)
            self._set_data(commands.VALVE_ACTUATION_TIME, actuation_time)
            # time.sleep(actuation_time / 1000)
        else:
            Logging.logger.error(
                "Error: acuation time out of range (5, 65535), inputted: %s",
                str(actuation_time),
            )
            raise ValueError("Error: Value entered for actuation time needs to be between 5 and 65535")

    def toggle_manual_trigger(self, toggle: bool) -> None:
        """
        Toggles the manual trigger to either on or off.

        Args:
            toggle (int): Bool value, 1 for on, 0 for off

        Returns:
            None

        Raises:
            NotImplementedError: Manual trigger is not implemented due to a firmware limitation.
        """
        # self._set_data(commands.MANUAL_TRIGGER, int(toggle))
        Logging.logger.warning(
            "toggle_manual_trigger() is not implemented: known firmware bug in PGVA-1 firmware <= 2.0.45"
        )
        raise NotImplementedError("""
                                  Manual trigger not implemented. There is a bug that exists in the PGVA-1 firmware <=2.0.45
                                  that prevents this function from working as intended
                                  """)

    def get_internal_sensor_data(self) -> dict:
        """
        Reads the internal Vacuum and Pressure chambers as well as the output pressure sensor.

        Args:
            None

        Returns:
            Dictionary of the sensor values
        """
        status = {}
        if self.version[0:3] != [2, 1, 3]:
            status["Extsensor"] = self._get_data(commands.EXTERNAL_SENSOR_VALUE)
        status["VacuumChamber"] = self.get_vacuum_chamber()
        status["PressureChamber"] = self.get_pressure_chamber()
        status["OutputPressure"] = self.get_output_pressure()
        Logging.logger.debug("Internal sensor data: %s", status)
        return status

    def get_vacuum_chamber(self) -> int:
        """
        Reads the internal vacuum chamber pressure.

        Args:
            None

        Returns:
            Vacuum chamber pressure in mBar
        """
        vacuum = self._get_data(commands.VACUUM_ACTUAL_MBAR)
        result = self._convert_twos_comp(vacuum, len(bin(vacuum)[2:]))
        Logging.logger.debug("Vacuum chamber reading: %s mBar", result)
        return result

    def get_pressure_chamber(self) -> int:
        """
        Reads the internal pressure chamber pressure.

        Args:
            None

        Returns:
            Pressure chamber pressure in mBar
        """
        result = self._get_data(commands.PRESSURE_ACTUAL_MBAR)
        Logging.logger.debug("Pressure chamber reading: %s mBar", result)
        return result

    def get_output_pressure(self) -> int:
        """
        Reads the output port pressure.

        Args:
            None

        Returns:
            Output pressure in mBar
        """
        pressure = self._get_data(commands.OUTPUT_PRESSURE_ACTUAL_MBAR)
        if pressure > 500:
            result = self._convert_twos_comp(pressure, len(bin(pressure)[2:]))
            Logging.logger.debug("Output pressure reading: %s mBar", result)
            return result
        Logging.logger.debug("Output pressure reading: %s mBar", pressure)
        return pressure

    def set_pressure_chamber(self, pressure: int) -> None:
        """
        Sets the internal pressure chamber.

        Args:
            pressure (int): Range between 200 ... 1000 mBar

        Returns:
            None

        Raises:
            ValueError: If pressure is outside the supported pressure chamber range.
        """
        if consts.MINIMUM_PRESSURE_CHAMBER_MBAR <= pressure <= consts.MAXIMUM_PRESSURE_CHAMBER_MBAR:
            # Using the pressure scaling factor provided via operation manual of the PGVA
            Logging.logger.info("Setting pressure chamber to %s mBar", pressure)
            pressure = int(pressure * consts.PRESSURE_CHAMBER_CONVERSION_FACTOR)
            self._set_data(commands.PRESSURE_THRESHOLD, pressure)
        else:
            err = f"Error: {pressure} input pressure outside of PGVA-1 working conditions. Please enter a value between 200 and 1000 mBar."
            Logging.logger.error(err)
            raise ValueError(err)

    def set_vacuum_chamber(self, vacuum: int) -> None:
        """
        Sets the internal vacuum chamber.

        Args:
            vacuum (int): Range between -200 ... -620 mBar

        Returns:
            None

        Raises:
            ValueError: If vacuum is outside the supported vacuum chamber range.
        """
        if consts.MINIMUM_VACUUM_CHAMBER_MBAR <= vacuum <= consts.MAXIMUM_VACUUM_CHAMBER_MBAR:
            Logging.logger.info("Setting vacuum chamber to %s mBar", vacuum)
            vacuum = int(vacuum * consts.VACUUM_CHAMBER_CONVERSION_FACTOR)
            self._set_data(commands.VACUUM_THRESHOLD, vacuum)
        else:
            err = f"Error: {vacuum} input pressure outside of PGVA-1 working conditions."
            Logging.logger.error(err)
            raise ValueError(err)

    def toggle_pump(self, toggle: bool) -> None:
        """
        Enables or disables the pump for creating pressure / vacuum.

        Args:
            toggle (bool): 1 for on, 0 for off

        Returns:
            None
        """
        Logging.logger.info("Toggling pump: %s", "ON" if toggle else "OFF")
        if self.version[0:3] != [2, 1, 3]:
            self._set_data(commands.PUMP_ENABLE, toggle)
        else:
            Logging.logger.info("PGVA firmware does not support the enable/disable pump function")

    def _validate_pump_enable(self):
        """
        Validates that the pump is enabled for creating pressure.

        Args:
            None

        Returns:
            Bool: True if enabled, False if disabled
        """
        if self.version[0:3] != [2, 1, 3]:
            if self._get_data_holding(commands.PUMP_ENABLE) == 1:
                Logging.logger.debug("Pump validation: pump is enabled")
                return True
            Logging.logger.warning("Pump is NOT enabled — call toggle_pump(True) before setting pressure")
            return False
        Logging.logger.info("PGVA firmware version does not support the enable/disable pump function")
        return True

    def _enable_pump(self):
        """
        Enables the pump.

        Args:
            None

        Returns:
            None
        """
        if self.version[0:3] != [2, 1, 3]:
            Logging.logger.info("Enabling pump")
            self._set_data(commands.PUMP_ENABLE, 1)
        else:
            Logging.logger.info("PGVA firmware does not support the enable/disable pump function")

    def _disable_pump(self):
        """
        Disables the pump.

        Args:
            None

        Returns:
            None
        """
        if self.version[0:3] != [2, 1, 3]:
            Logging.logger.info("Disabling pump")
            self._set_data(commands.PUMP_ENABLE, 0)
        else:
            Logging.logger.info("connected PGVA device version does not support this function ")

    def print_driver_information(self) -> None:
        """
        Prints all parameters.

        Args:
            None

        Returns:
            None
        """
        internal_data = self.get_internal_sensor_data()
        print("Driver Information:")
        print(f"* Firmware version: {self.version}")
        print(f"* Connection type: {self._config.interface}")
        print(f"* {internal_data}")

    def get_status_word(self) -> dict:
        """
        Reads the status word and outputs it to the log.

        Args:
            None

        Returns:
            Current status of the PGVA-1
        """
        pgva_status = self._get_data(commands.STATUS_WORD)
        status_word = {
            "Status": self._status["Status"][pgva_status & 1],
            "Pump": self._status["Pump"][(pgva_status >> 1) & 0b11],
            "Pressure": self._status["Pressure"][(pgva_status >> 3) & 1],
            "Vacuum": self._status["Vacuum"][(pgva_status >> 4) & 1],
            "EEPROM": self._status["EEPROM"][(pgva_status >> 5) & 1],
            "TargetPressure": self._status["TargetPressure"][(pgva_status >> 6) & 1],
            "Trigger": self._status["Trigger"][(pgva_status >> 7) & 1],
            "OutputValveControl": self._status["OutputValveControl"][(pgva_status >> 10) & 1],
            "OutputValve": self._status["OutputValve"][(pgva_status >> 11) & 1],
        }

        Logging.logger.debug("Status word: %s", status_word)
        return status_word

    def get_warning_word(self) -> dict:
        """
        Reads the warning word and outputs it to the log.

        Args:
            None

        Returns:
           Current warning word of the PGVA-1
        """
        pgva_warning = self._get_data(commands.WARNING_WORD)
        warning_word = {
            "SupplyVoltage": self._warning["SupplyVoltage"][pgva_warning & 1],
            "VacuumThreshold": self._warning["VacuumThreshold"][(pgva_warning >> 1) & 1],
            "PressureThreshold": self._warning["PressureThreshold"][(pgva_warning >> 2) & 1],
            "TargetPressure": self._warning["TargetPressure"][(pgva_warning >> 4) & 1],
            "VacuumChamber": self._warning["VacuumChamber"][(pgva_warning >> 5) & 1],
            "Pump": self._warning["Pump"][(pgva_warning >> 7) & 1],
            "ExternalSensor": self._warning["ExternalSensor"][(pgva_warning >> 9) & 1],
        }
        if any(v != "Reset" for v in warning_word.values()):
            Logging.logger.warning("Active PGVA warning(s): %s", warning_word)
        else:
            Logging.logger.debug("Warning word: %s", warning_word)
        return warning_word

    def get_error_word(self) -> dict:
        """
        Reads the error word and outputs it to the log.

        Args:
            None

        Returns:
            Current error word of the PGVA-1
        """
        pgva_error = self._get_data(commands.ERROR_WORD)
        error_word = {
            "PumpTimeout": self._pgva_error["PumpTimeout"][pgva_error & 1],
            "TimeoutPressure": self._pgva_error["TimeoutPressure"][(pgva_error >> 1) & 1],
            "ModbusError": self._pgva_error["ModbusError"][(pgva_error >> 2) & 1],
            "LowVoltage": self._pgva_error["LowVoltage"][(pgva_error >> 3) & 1],
            "HighVoltage": self._pgva_error["HighVoltage"][(pgva_error >> 4) & 1],
            "TimeoutExternalSensor": self._pgva_error["TimeoutExternalSensor"][(pgva_error >> 5) & 1],
        }
        if any(v != "Reset" for v in error_word.values()):
            Logging.logger.error("Active PGVA error(s): %s", error_word)
        else:
            Logging.logger.debug("Error word: %s", error_word)
        return error_word

    def get_modbus_error_word(self) -> dict:
        """
        Reads the modbus error word and outputs it to the log.

        Args:
            None

        Returns:
            Current modbus error word of the PGVA-1
        """
        modbus_error = self._get_data(commands.LAST_MODBUS_ERROR)
        modbus_error_word = {"OutputActuationTime": self._modbus_error["OutputActuationTime"][modbus_error & 1]}
        if any(v != "Reset" for v in modbus_error_word.values()):
            Logging.logger.error("Active Modbus error(s): %s", modbus_error_word)
        else:
            Logging.logger.debug("Modbus error word: %s", modbus_error_word)
        return modbus_error_word

    def _set_pgva_status(self):
        """
        Sets the internal messages for the incoming status word.

        Args:
            None

        Returns:
            None
        """
        self._status = {
            "Status": {0: "Idle", 1: "Busy"},
            "Pump": {
                0: "Pump is off",
                1: "Pump is building pressure",
                2: "Pump is building vacuum",
            },
            "Pressure": {
                0: "Pressure in the tank is nominal",
                1: "Pressure in the tank is below threshold",
            },
            "Vacuum": {
                0: "Vacuum in the tank is nominal",
                1: "Vacuum in the tank is below threshold",
            },
            "EEPROM": {0: "No EEPROM write pending", 1: "EEPROM write pending"},
            "TargetPressure": {
                0: "Target pressure in progress",
                1: "Target pressure achieved",
            },
            "Trigger": {0: "Trigger is closed", 1: "Trigger is open"},
            "OutputValveControl": {
                0: "Exhaust valve management disabled",
                1: "Exhaust valve management enabled",
            },
            "OutputValve": {0: "Exhaust valve closed", 1: "Exhaust valve open"},
        }

    def _set_pgva_warning(self):
        """
        Sets the internal messages for the incoming warning word.

        Args:
            None

        Returns:
            None
        """
        self._warning = {
            "SupplyVoltage": {0: "Reset", 1: "Abnormal supply voltage"},
            "VacuumThreshold": {
                0: "Reset",
                1: "Vacuum generator cannot reach threshold",
            },
            "PressureThreshold": {
                0: "Reset",
                1: "Pressure generator cannot reach threshold",
            },
            "TargetPressure": {
                0: "Reset",
                1: "Preset output pressure cannot be reached",
            },
            "VacuumChamber": {0: "Reset", 1: "Vacuum chamber set below -500 mBar"},
            "PressureChamber": {0: "Reset", 1: "Pressure chamber set above 500 mBar"},
            "Pump": {0: "Reset", 1: "Pump ran for 9 minutes"},
            "ExternalSensor": {0: "Reset", 1: "External Sensor Verification warning"},
        }

    def _set_pgva_error(self):
        """
        Sets the internal messages for the incoming error word.

        Args:
            None

        Returns:
            None
        """
        self._pgva_error = {
            "PumpTimeout": {0: "Reset", 1: "Pump ran longer than 10 minutes"},
            "TimeoutPressure": {
                0: "Reset",
                1: "Target output pressure not achieved in 8 minutes",
            },
            "ModbusError": {
                0: "Reset",
                1: "Modbus error occurred, please read modbus error word",
            },
            "LowVoltage": {0: "Reset", 1: "Power supply too low"},
            "HighVoltage": {0: "Reset", 1: "Power supply too high"},
            "TimeoutExternalSensor": {0: "Reset", 1: "External sensor check timed out"},
        }

    def _set_modbus_error(self):
        """
        Sets the internal messages for the incoming modbus error word.

        Args:
            None

        Returns:
            None
        """
        modbus_message = "The Modbus command was not executed"
        self._modbus_error = {
            "OutputActuationTime": {
                0: "Reset",
                1: f"Trigger time is outside of input range, {modbus_message}",
            },
            "PressureThreshold": {
                0: "Reset",
                1: f"Pressure threshold outside of input range, {modbus_message}",
            },
            "VacuumThreshold": {
                0: "Reset",
                1: f"Vacuum threshold outside of input range, {modbus_message}",
            },
            "OutputPressure": {
                0: "Reset",
                1: f"OutputPressure is outside of input range, {modbus_message}",
            },
            "ModbusID": {
                0: "Reset",
                1: f"Modbus Unit ID out of range, {modbus_message}",
            },
            "IPAddress": {
                0: "Reset",
                1: f"IP address does not comply with the restrictions, {modbus_message}",
            },
            "ManualTrigger": {
                0: "Reset",
                1: f"Manual trigger input is invalid, {modbus_message}",
            },
            "IncorrectNumberRegisters": {
                0: "Reset",
                1: f"Invalid number of registers can be written, {modbus_message}",
            },
            "Register": {
                0: "Reset",
                1: f"""Register is write protected and cannot be written to,
                         {modbus_message}""",
            },
            "DHCP": {
                0: "Reset",
                1: f"""Input values are outside of the permissable range,
                     {modbus_message}""",
            },
            "ExternalSensor": {
                0: "Reset",
                1: f"""The input values are outside of the permissable range,
                               {modbus_message}""",
            },
            "ExhaustValveVolume": {
                0: "Reset",
                1: f"""The input values are outside of the permissable range,
                                   {modbus_message}""",
            },
        }

    def _convert_twos_comp(self, val, bits):
        """
        Converts a 2 compliment value into the actual signed integer value.

        Args:
            val: value
            bits: number of bits

        Returns:
            Converted signed integer value
        """
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val


class PGVAModbusTCP(PGVAModbusClient):
    """
    This class is the interface backend for using Modbus TCP communication.

    TODO: Add typical usage example
    """

    def __init__(self, config: PGVAConfig) -> None:
        """
        TCP Client Interface Constructor.

        Args:
            config (PGVATCPConfig): A configuration class designated for ModbusTCP

        Returns:
            None

        Raises:
            TypeError: If config is not an instance of PGVATCPConfig.
        """
        super().__init__(config)
        if not isinstance(config, PGVATCPConfig):
            raise TypeError(
                f"""Error: Config does not match the ModbusTCP backend.
                The type passed in was: {type(config)}"""
            )
        try:
            self._config = config
            self.client = ModbusTcpClient(host=self._config.ip, port=self._config.port)
            self._set_modbus_error()
            self._set_pgva_error()
            self._set_pgva_status()
            self._set_pgva_warning()
            self.version = self.get_firmware_version()
            Logging.logger.info(
                "PGVA connected via TCP — host: %s, port: %s, unit_id: %s, firmware: %s",
                self._config.ip,
                self._config.port,
                self._config.unit_id,
                self.version,
            )
        except socket.error as socket_error:
            Logging.logger.error("Socket error: %s. ", str(socket_error))
            Logging.logger.info(self._config)

    def print_driver_information(self) -> None:
        """
        Display all available information about the PGVA driver.

        Args:
            None

        Returns:
            None
        """
        super().print_driver_information()
        print(f"* IP Address: {self._config.ip}")
        print(f"* Port: {self._config.port}")
        print(f"* Modbus Slave ID: {self._config.unit_id}")


class PGVAModbusSerial(PGVAModbusClient):
    """This class is the interface backend for using Modbus Serial communication."""

    def __init__(self, config: PGVAConfig) -> None:
        """
        Serial Client Interface Constructor.

        Args:
            config (PGVASerialConfig): A configuration class designated for ModbusSerial

        Returns:
            None

        Raises:
            TypeError: If config is not an instance of PGVASerialConfig.
        """
        Logging.logger.warning("""The Modbus Serial connection mode is currently experimental and under active development.
                                It can currently only be instantiated directly.
                                Use at your own risk.""")
        super().__init__(config)
        if not isinstance(config, PGVASerialConfig):
            raise TypeError(
                f"""Error: Config does not match the ModbusSerial backend.
                            The type passed in was: {type(config)}"""
            )
        try:
            self._config = config
            self.client = ModbusSerialClient(port=self._config.com_port, baudrate=self._config.baudrate)
            self.version = self.get_firmware_version()
            self._set_modbus_error()
            self._set_pgva_error()
            self._set_pgva_status()
            self._set_pgva_warning()
            Logging.logger.info(
                "PGVA connected via Serial — port: %s, baudrate: %s, unit_id: %s, firmware: %s",
                self._config.com_port,
                self._config.baudrate,
                self._config.unit_id,
                self.version,
            )
        except RuntimeError as run_err:
            Logging.logger.error("Error with serial connection: %s", str(run_err))
            Logging.logger.info(self._config)

    def print_driver_information(self) -> None:
        """
        Display all available information about the PGVA driver.

        Args:
            None

        Returns:
            None
        """
        super().print_driver_information()
        print(f"* Serial Port: {self._config.com_port}")
        print(f"* Baudrate: {self._config.baudrate}")
        print(f"* Modbus Slave ID: {self._config.unit_id}")
