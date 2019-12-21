"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from typing import Any, Optional, Dict, Union

from platypush.plugins import Plugin, action


class GpioPlugin(Plugin):
    """
    Plugin to handle raw read/write operation on the Raspberry Pi GPIO pins.

    Requires:
        * **RPi.GPIO** (`pip install RPi.GPIO`)
    """

    def __init__(self, pins: Optional[Dict[str, int]] = None, mode: str = 'board', **kwargs):
        """
        :param mode: Specify 'board' if you want to use the board PIN numbers,
            'bcm' for Broadcom PIN numbers (default: 'board')
        :param pins: Configuration for the GPIO PINs as a name -> pin_number map.

        Example::

            {
                "LED_1": 14,
                "LED_2": 15,
                "MOTOR": 16,
                "SENSOR": 17
            }

        """

        super().__init__(**kwargs)
        self.mode = self._get_mode(mode)
        self.pins_by_name = pins if pins else {}
        self.pins_by_number = {number: name
                               for (name, number) in self.pins_by_name.items()}

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
        import RPi.GPIO as gpio

        mode_str = mode_str.upper()
        assert mode_str in ['BOARD', 'BCM'], 'Invalid mode: {}'.format(mode_str)
        return getattr(gpio, mode_str)

    @action
    def write(self, pin: Union[int, str], value: Union[int, bool],
            name: Optional[str] = None, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Write a byte value to a pin.

        :param pin: PIN number or configured name
        :param name: Optional name for the written value (e.g. "temperature" or "humidity")
        :param value: Value to write
        :param mode: If a PIN number is specified then you can override the default 'mode'
            default parameter

        Response::

            output = {
                "name": <pin or metric name>,
                "pin": <pin>,
                "value": <value>,
                "method": "write"
            }
        """

        import RPi.GPIO as gpio

        name = name or pin
        pin = self._get_pin_number(pin)
        mode = self._get_mode(mode) if mode else self.mode
        gpio.setmode(mode)
        gpio.setup(pin, gpio.OUT)
        gpio.output(pin, value)

        return {
            'name': name,
            'pin': pin,
            'value': value,
            'method': 'write',
        }

    @action
    def read(self, pin: Union[int, str], name: Optional[str] = None,
            mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Reads a value from a PIN.

        :param pin: PIN number or configured name.
        :param name: Optional name for the read value (e.g. "temperature" or "humidity")
        :param mode: If a PIN number is specified then you can override the default 'mode'
            default parameter

        Response::

            output = {
                "name": <pin number or pin/metric name>,
                "pin": <pin>,
                "value": <value>,
                "method": "read"
            }
        """

        import RPi.GPIO as gpio

        name = name or pin
        pin = self._get_pin_number(pin)
        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.IN)
        val = gpio.input(pin)

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
        for (pin, name) in self.pins_by_number.items():
            values.append(self.read(pin=pin, name=name).output)

        return values

    @action
    def cleanup(self):
        import RPi.GPIO as gpio
        gpio.cleanup()


# vim:sw=4:ts=4:et:
