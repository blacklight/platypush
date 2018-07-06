"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import threading
import time

from platypush.plugins import Plugin, action


class GpioPlugin(Plugin):
    """
    Plugin to handle raw read/write operation on the Raspberry Pi GPIO pins.

    Requires:
        * **RPi.GPIO** (`pip install RPi.GPIO`)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def write(self, pin, val):
        """
        Write a byte value to a pin.

        :param pin: PIN number
        :type pin: int

        :param val: Value to write
        :type val: int

        :returns: dict

        Response::

            output = {
                "pin": <pin>,
                "val": <val>,
                "method": "write"
            }
        """

        import RPi.GPIO as gpio

        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.OUT)
        gpio.output(pin, val)

        return {
            'pin': pin,
            'val': val,
            'method': 'write',
        }

    @action
    def read(self, pin):
        """
        Reads a value from a PIN.

        :param pin: PIN number
        :type pin: int

        :returns: dict

        Response::

            output = {
                "pin": <pin>,
                "val": <val>,
                "method": "read"
            }
        """

        import RPi.GPIO as gpio

        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.IN)
        val = gpio.input(pin)

        return {
            'pin': pin,
            'val': val,
            'method': 'read',
        }


# vim:sw=4:ts=4:et:

