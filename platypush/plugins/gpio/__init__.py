import threading
from typing import Any, Optional, Dict, Union, Collection

from platypush.context import get_bus
from platypush.message.event.gpio import GPIOEvent
from platypush.plugins import RunnablePlugin, action


class GpioPlugin(RunnablePlugin):
    """
    This plugin can be used to interact with custom electronic devices
    connected to a Raspberry Pi (or compatible device) over GPIO pins.

    Requires:

        * **RPi.GPIO** (``pip install RPi.GPIO``)

    Triggers:

        * :class:`platypush.message.event.gpio.GPIOEvent` when the value of a
            monitored PIN changes.

    """

    def __init__(
        self,
        pins: Optional[Dict[str, int]] = None,
        monitored_pins: Optional[Collection[Union[str, int]]] = None,
        mode: str = 'board',
        **kwargs
    ):
        """
        :param mode: Specify ``board`` if you want to use the board PIN numbers,
            ``bcm`` for Broadcom PIN numbers (default: ``board``)
        :param pins: Custom `GPIO name` -> `PIN number` mapping. This can be
            useful if you want to reference your GPIO ports by name instead
            of PIN number.

        Example:

          .. code-block:: yaml

            pins:
                LED_1: 14,
                LED_2: 15,
                MOTOR: 16,
                SENSOR_1: 17
                SENSOR_2: 18

        :param monitored_pins: List of PINs to monitor. If a new value is detected
            on these pins then a :class:`platypush.message.event.gpio.GPIOEvent`
            event will be triggered. GPIO PINS can be referenced either by number
            or name, if a name is specified on the `pins` argument.
        """

        super().__init__(**kwargs)
        self.mode = self._get_mode(mode)
        self._initialized = False
        self._init_lock = threading.RLock()
        self._initialized_pins = {}
        self._monitored_pins = monitored_pins or []
        self.pins_by_name = pins if pins else {}
        self.pins_by_number = {
            number: name for (name, number) in self.pins_by_name.items()
        }

    def _init_board(self):
        import RPi.GPIO as GPIO

        with self._init_lock:
            if self._initialized and GPIO.getmode():
                return

            GPIO.setmode(self.mode)
            self._initialized = True

    def _get_pin_number(self, pin):
        try:
            pin = int(str(pin))
        except ValueError:
            pin = self.pins_by_name.get(pin)
            if not pin:
                raise RuntimeError('Unknown PIN name: "{}"'.format(pin))

        return pin

    @staticmethod
    def _get_mode(mode_str: str) -> int:
        import RPi.GPIO as GPIO

        mode_str = mode_str.upper()
        assert mode_str in ['BOARD', 'BCM'], 'Invalid mode: {}'.format(mode_str)
        return getattr(GPIO, mode_str)

    def on_gpio_event(self):
        def callback(pin: int):
            import RPi.GPIO as GPIO

            value = GPIO.input(pin)
            pin = self.pins_by_number.get(pin, pin)
            get_bus().post(GPIOEvent(pin=pin, value=value))

        return callback

    def main(self):
        import RPi.GPIO as GPIO

        if not self._monitored_pins:
            return  # No need to start the monitor

        self._init_board()
        monitored_pins = [self._get_pin_number(pin) for pin in self._monitored_pins]

        for pin in monitored_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.on_gpio_event())

        self.wait_stop()

    @action
    def write(
        self, pin: Union[int, str], value: Union[int, bool], name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Write a byte value to a pin.

        :param pin: PIN number or configured name
        :param name: Optional name for the written value (e.g. "temperature" or "humidity")
        :param value: Value to write

        Response::

            output = {
                "name": <pin or metric name>,
                "pin": <pin>,
                "value": <value>,
                "method": "write"
            }
        """

        import RPi.GPIO as GPIO

        self._init_board()
        name = name or pin
        pin = self._get_pin_number(pin)

        if pin not in self._initialized_pins or self._initialized_pins[pin] != GPIO.OUT:
            GPIO.setup(pin, GPIO.OUT)
            self._initialized_pins[pin] = GPIO.OUT

        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, value)

        return {
            'name': name,
            'pin': pin,
            'value': value,
            'method': 'write',
        }

    @action
    def read(self, pin: Union[int, str], name: Optional[str] = None) -> Dict[str, Any]:
        """
        Reads a value from a PIN.

        :param pin: PIN number or configured name.
        :param name: Optional name for the read value (e.g. "temperature" or "humidity")

        Response::

            output = {
                "name": <pin number or pin/metric name>,
                "pin": <pin>,
                "value": <value>,
                "method": "read"
            }
        """

        import RPi.GPIO as GPIO

        self._init_board()
        name = name or pin
        pin = self._get_pin_number(pin)

        if pin not in self._initialized_pins:
            GPIO.setup(pin, GPIO.IN)
            self._initialized_pins[pin] = GPIO.IN

        val = GPIO.input(pin)

        return {
            'name': name,
            'pin': pin,
            'value': val,
            'method': 'read',
        }

    @action
    def get_measurement(self, pin=None):
        if pin is None:
            return self.read_all()
        return self.read(pin)

    @action
    def read_all(self):
        """
        Reads the values from all the configured PINs and returns them as a list. It will raise a RuntimeError if no
        PIN mappings were configured.
        """

        if not self.pins_by_number:
            raise RuntimeError("No PIN mappings were provided/configured")

        values = []
        for pin, name in self.pins_by_number.items():
            # noinspection PyUnresolvedReferences
            values.append(self.read(pin=pin, name=name).output)

        return values

    @action
    def cleanup(self):
        """
        Cleanup the state of the GPIO and resets PIN values.
        """
        import RPi.GPIO as GPIO

        with self._init_lock:
            if self._initialized:
                GPIO.cleanup()
                self._initialized_pins = {}
                self._initialized = False


# vim:sw=4:ts=4:et:
