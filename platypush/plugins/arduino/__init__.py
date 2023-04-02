import enum
import time

from typing import List, Optional, Dict, Union, Callable, Tuple, Type
from typing_extensions import override

from pyfirmata2 import (
    Arduino,
    ArduinoMega,
    ArduinoDue,
    ArduinoNano,
    Board,
    Pin,
    util,
    ANALOG,
    INPUT,
    PWM,
)

from platypush.common.sensors import Numeric
from platypush.entities.devices import Device
from platypush.entities.sensors import NumericSensor
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


class PinType(enum.IntEnum):
    """
    PIN type enumeration (analog or digital).
    """

    ANALOG = 1
    DIGITAL = 2


class BoardType(enum.Enum):
    """
    Board types.
    """

    MEGA = 'mega'
    DUE = 'due'
    NANO = 'nano'


# pylint: disable=too-many-ancestors
class ArduinoPlugin(SensorPlugin):
    """
    Interact with an Arduino connected to the host machine over USB using the
    `Firmata <https://www.arduino.cc/en/reference/firmata>`_ protocol.

    You have two options to communicate with an Arduino-compatible board over USB:

        - Use this plugin if you want to use the general-purpose Firmata protocol - in this case most of your
          processing logic will be on the host side and you can read/write data to the Arduino transparently.
        - Use the :class:`platypush.plugins.serial.SerialPlugin` if instead you want to run more custom logic
          on the Arduino and communicate back with the host computer through JSON formatted messages.

    Download and flash the
    `Standard Firmata <https://github.com/firmata/arduino/blob/master/examples/StandardFirmata/StandardFirmata.ino>`_
    firmware to the Arduino in order to use this plugin.

    Requires:

        * **pyfirmata2** (``pip install pyfirmata2``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    def __init__(
        self,
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: int = 9600,
        analog_pins: Optional[Dict[str, int]] = None,
        digital_pins: Optional[Dict[str, int]] = None,
        timeout: float = 20.0,
        conv_functions: Optional[Dict[Union[str, int], Union[str, Callable]]] = None,
        poll_interval: float = 1.0,
        **kwargs,
    ):
        """
        :param board: Default board name or path (e.g. ``COM3`` on Windows or ``/dev/ttyUSB0`` on Unix). If not set
            then the plugin will attempt an auto-discovery.

        :param board_type: Default board type. It can be 'mega', 'due' or 'nano'. Leave empty for auto-detection.
        :param baud_rate: Default serial baud rate (default: 9600)
        :param analog_pins: Optional analog PINs map name->pin_number.
        :param digital_pins: Optional digital PINs map name->pin_number.
        :param timeout: Board communication timeout in seconds.
        :param conv_functions: Optional mapping of conversion functions to apply to the analog values read from a
            certain PIN. The key can either be the PIN number or the name as specified in ``analog_pins``, the value
            can be a function that takes an argument and transforms it or its lambda string representation.
            Note that ``analog_read`` returns by default float values in the range [0.0, 1.0]. Example:

            .. code-block:: yaml

                arduino:
                    board: /dev/ttyUSB0
                    analog_pins:
                        temperature: 1  # Analog PIN 1

                    conv_functions:
                        temperature: 'lambda t: t * 500.0'

        """
        super().__init__(poll_interval=poll_interval, **kwargs)

        self.board = board
        self.board_type = self._get_board_type(board_type)
        self.baud_rate = baud_rate
        self.timeout = timeout

        self._pin_number_by_name = {
            PinType.ANALOG: analog_pins or {},
            PinType.DIGITAL: digital_pins or {},
        }

        self._pin_name_by_number = {
            PinType.ANALOG: {
                number: name
                for name, number in self._pin_number_by_name[PinType.ANALOG].items()
            },
            PinType.DIGITAL: {
                number: name
                for name, number in self._pin_number_by_name[PinType.DIGITAL].items()
            },
        }

        self.conv_functions: Dict[Union[str, int], Callable] = {
            (self._pin_number_by_name[PinType.ANALOG].get(str(pin), pin)): (
                f if callable(f) else eval(f)
            )
            for pin, f in (conv_functions or {}).items()
        }

        self._boards: Dict[str, Board] = {}
        self._board_iterators: Dict[str, util.Iterator] = {}

    @staticmethod
    def _get_board_type(board_type: Optional[str] = None) -> Type[Board]:
        if not board_type:
            return Arduino

        board_type = board_type.lower()
        if board_type == BoardType.DUE.value:
            return ArduinoDue
        if board_type == BoardType.NANO.value:
            return ArduinoNano
        if board_type == BoardType.MEGA.value:
            return ArduinoMega

        raise AssertionError(f'Invalid board_type: {board_type}')

    def _get_board(
        self,
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> Board:
        board_name = board or self.board or Arduino.AUTODETECT
        baud_rate = baud_rate or self.baud_rate
        timeout = timeout or self.timeout

        if board_name in self._boards:
            return self._boards[board_name]

        board_obj_type = (
            self._get_board_type(board_type) if board_type else self.board_type
        )
        assert board_obj_type

        board_obj = board_obj_type(board_name, baudrate=baud_rate, timeout=timeout)
        board_name = board_obj.name or ''
        self.logger.info('Connected to board %s', board_name)
        self._boards[board_name] = board_obj
        self._board_iterators[board_name] = util.Iterator(board_obj)
        self._board_iterators[board_name].start()
        return board_obj

    def _get_board_and_pin(
        self,
        pin: Union[int, str],
        pin_type: PinType,
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[Board, int]:
        board_ = self._get_board(
            board, board_type=board_type, baud_rate=baud_rate, timeout=timeout
        )
        if pin in self._pin_number_by_name[pin_type]:
            pin = self._pin_number_by_name[pin_type][str(pin)]

        assert isinstance(pin, int), f'Invalid PIN number/name: {pin}'
        return board_, pin

    @staticmethod
    def _get_pin(pin: int, board: Board, pin_type: PinType) -> Pin:
        pins = None
        if pin_type == PinType.ANALOG:
            pins = board.analog
        if pin_type == PinType.DIGITAL:
            pins = board.digital

        assert pins, f'Invalid pin_type: {pin_type}'

        if pins[pin].mode in [ANALOG, INPUT]:
            pins[pin].enable_reporting()
        return pins[pin]

    def _poll_value(
        self,
        pin: int,
        board: Board,
        pin_type: PinType,
        timeout: Optional[float] = None,
    ) -> Optional[Union[bool, float]]:
        value = None
        poll_start = time.time()

        while value is None:
            if timeout and time.time() - poll_start >= timeout:
                raise RuntimeError('Read timeout')

            pin_ = self._get_pin(pin=pin, board=board, pin_type=pin_type)
            if pin_.mode not in [INPUT, ANALOG]:
                self.logger.warning(
                    'PIN %d is not configured in input/analog mode', pin
                )
                return None

            value = pin_.read()
            if value is None:
                time.sleep(0.001)

        if pin_type == PinType.DIGITAL:
            value = bool(value)

        return value

    @action
    def analog_read(
        self,
        pin: Union[int, str],
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        conv_function: Optional[Union[str, Callable]] = None,
        timeout: Optional[int] = None,
    ) -> Optional[float]:
        """
        Read an analog value from a PIN.

        :param pin: PIN number or configured name.
        :param board: Board path or name (default: default configured ``board``).
        :param board_type: Board type. It can be 'mega', 'due' or 'nano' (default: configured ``board_type``).
        :param baud_rate: Baud rate (default: default configured ``baud_rate``).
        :param conv_function: Optional conversion function override to apply to the output. It can be either a function
            object or its lambda string representation (e.g. ``lambda x: x*x``). Keep in mind that ``analog_read``
            returns by default float values in the range ``[0.0, 1.0]``.
        :param timeout: Communication timeout in seconds (default: default configured ``timeout``).
        """
        board_, pin = self._get_board_and_pin(
            pin=pin,
            pin_type=PinType.ANALOG,
            board=board,
            board_type=board_type,
            baud_rate=baud_rate,
            timeout=timeout,
        )

        conv_function = conv_function or self.conv_functions.get(pin)
        converter: Optional[Callable[[float], float]] = None
        if isinstance(conv_function, str):
            converter = eval(conv_function)
        elif callable(conv_function):
            converter = conv_function
        elif conv_function is not None:
            raise AssertionError(
                'Expected conv_function to be null, a string or a function, '
                f'got "{conv_function}" instead'
            )

        value = self._poll_value(
            pin=pin, board=board_, pin_type=PinType.ANALOG, timeout=timeout
        )

        if converter and value is not None:
            value = converter(value)
        return value

    @action
    def digital_read(
        self,
        pin: Union[int, str],
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Read a digital value from a PIN.

        :param pin: PIN number or configured name.
        :param board: Board path or name (default: default configured ``board``).
        :param board_type: Board type. It can be 'mega', 'due' or 'nano' (default: configured ``board_type``).
        :param baud_rate: Baud rate (default: default configured ``baud_rate``).
        :param timeout: Communication timeout in seconds (default: default configured ``timeout``).
        """
        board_, pin = self._get_board_and_pin(
            pin=pin,
            pin_type=PinType.DIGITAL,
            board=board,
            board_type=board_type,
            baud_rate=baud_rate,
            timeout=timeout,
        )

        return bool(
            self._poll_value(
                pin=pin, board=board_, pin_type=PinType.DIGITAL, timeout=timeout
            )
        )

    @action
    def analog_write(
        self,
        pin: Union[int, str],
        value: float,
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        """
        Write a value to an analog PIN.

        :param pin: PIN number or configured name.
        :param value: Voltage to be sent, a real number normalized between 0 and 1.
        :param board: Board path or name (default: default configured ``board``).
        :param board_type: Board type. It can be 'mega', 'due' or 'nano' (default: configured ``board_type``).
        :param baud_rate: Baud rate (default: default configured ``baud_rate``).
        :param timeout: Communication timeout in seconds (default: default configured ``timeout``).
        """
        board_, pin = self._get_board_and_pin(
            pin=pin,
            pin_type=PinType.ANALOG,
            board=board,
            board_type=board_type,
            baud_rate=baud_rate,
            timeout=timeout,
        )
        board_.analog[pin].write(value)

    @action
    def digital_write(
        self,
        pin: Union[int, str],
        value: bool,
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        """
        Write a value to a digital PIN.

        :param pin: PIN number or configured name.
        :param value: True (HIGH) or False (LOW).
        :param board: Board path or name (default: default configured ``board``).
        :param board_type: Board type. It can be 'mega', 'due' or 'nano' (default: configured ``board_type``).
        :param baud_rate: Baud rate (default: default configured ``baud_rate``).
        :param timeout: Communication timeout in seconds (default: default configured ``timeout``).
        """
        board_, pin = self._get_board_and_pin(
            pin=pin,
            pin_type=PinType.DIGITAL,
            board=board,
            board_type=board_type,
            baud_rate=baud_rate,
            timeout=timeout,
        )
        board_.digital[pin].write(value)

    @action
    def pwm_write(
        self,
        pin: Union[int, str],
        value: float,
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        """
        Write a PWM value to a digital PIN.

        :param pin: PIN number or configured name.
        :param value: PWM real value normalized between 0 and 1.
        :param board: Board path or name (default: default configured ``board``).
        :param board_type: Board type. It can be 'mega', 'due' or 'nano' (default: configured ``board_type``).
        :param baud_rate: Baud rate (default: default configured ``baud_rate``).
        :param timeout: Communication timeout in seconds (default: default configured ``timeout``).
        """
        board_, pin = self._get_board_and_pin(
            pin=pin,
            pin_type=PinType.DIGITAL,
            board=board,
            board_type=board_type,
            baud_rate=baud_rate,
            timeout=timeout,
        )

        assert board_.digital[pin].PWM_CAPABLE, f'PIN {pin} is not PWM capable'
        if board_.digital[pin] != PWM:
            board_.digital[pin].mode = PWM
            time.sleep(0.001)  # 1 μs spike to activate a PWM pin

        board_.digital[pin].write(value)

    @action
    def get_measurement(
        self,
        *_,
        board: Optional[str] = None,
        board_type: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout: Optional[int] = None,
        **__,
    ) -> Dict[str, Optional[Union[float, bool]]]:
        """
        Get a measurement from all the configured PINs.

        :param board: Board path or name (default: default configured ``board``)
        :param board_type: Board type. It can be 'mega', 'due' or 'nano' (default: configured ``board_type``).
        :param baud_rate: Baud rate (default: default configured ``baud_rate``)
        :param timeout: Communication timeout in seconds (default: default configured ``timeout``).
        :return: dict, where the keys are either the configured names of the PINs (see ``analog_pins`` configuration)
            or all the analog PINs (names will be in the format 'A0..A7' in that case), and the values will be the
            real values measured, either normalized between 0 and 1 if no conversion functions were provided, or
            transformed through the configured ``conv_functions``.
        """
        ret = {}
        board_ = self._get_board(
            board=board, board_type=board_type, baud_rate=baud_rate, timeout=timeout
        )

        assert board_, f'No such board: board={board}, board_type={board_type}'

        for pin in board_.analog:
            if (
                self._pin_name_by_number[PinType.ANALOG]
                and pin.pin_number not in self._pin_name_by_number[PinType.ANALOG]
            ):
                continue

            name = self._pin_name_by_number[PinType.ANALOG].get(
                pin.pin_number, f'A{pin.pin_number}'
            )
            value = self._poll_value(
                pin=pin.pin_number,
                board=board_,
                pin_type=PinType.ANALOG,
                timeout=timeout or self.timeout,
            )

            if value is None:
                continue

            conv_function = self.conv_functions.get(
                name, self.conv_functions.get(pin.pin_number)
            )
            if conv_function:
                value = conv_function(value)

            ret[name] = value

        return ret

    @override
    def transform_entities(self, entities: Dict[str, Numeric]) -> List[Device]:  # type: ignore
        dev_id = 'arduino'
        dev_name = 'Arduino'
        if self.board:
            dev_id += f':{self.board}'
            dev_name += f' @ {self.board}'

        return [
            Device(
                id=dev_id,
                name=dev_name,
                children=[
                    NumericSensor(
                        id=f'{dev_id}:{key}',
                        name=key,
                        value=value,
                    )
                    for key, value in entities.items()
                ],
            )
        ]

    @action
    def stop(self):
        super().stop()
        for it in self._board_iterators.values():
            it.stop()

        for board in self._boards.values():
            board.exit()

        self._board_iterators = {}
        self._boards = {}


# vim:sw=4:ts=4:et:
