"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from platypush.plugins import Plugin, action


class GpioPlugin(Plugin):
    """
    Plugin to handle raw read/write operation on the Raspberry Pi GPIO pins.

    Requires:
        * **RPi.GPIO** (`pip install RPi.GPIO`)
    """

    def __init__(self, pins=None, **kwargs):
        """
        :param pins: Configuration for the GPIO PINs as a name -> pin_number map.
        :type pins: dict

        Example::

            {
                "LED_1": 14,
                "LED_2": 15,
                "MOTOR": 16,
                "SENSOR": 17
            }
        """

        super().__init__(**kwargs)
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

    @action
    def write(self, pin, value, name=None):
        """
        Write a byte value to a pin.

        :param pin: PIN number or configured name
        :type pin: int or str

        :param name: Optional name for the written value (e.g. "temperature" or "humidity")
        :type name: str

        :param value: Value to write
        :type value: int

        :returns: dict

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
        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.OUT)
        gpio.output(pin, value)

        return {
            'name': name,
            'pin': pin,
            'value': value,
            'method': 'write',
        }

    @action
    def read(self, pin, name=None):
        """
        Reads a value from a PIN.

        :param pin: PIN number or configured name.
        :type pin: int or str

        :param name: Optional name for the read value (e.g. "temperature" or "humidity")
        :type name: str

        :returns: dict

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


# vim:sw=4:ts=4:et:
