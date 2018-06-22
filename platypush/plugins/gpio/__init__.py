"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import threading
import time

from platypush.message.response import Response
from platypush.plugins import Plugin


class GpioPlugin(Plugin):
    """
    Plugin to handle raw read/write operation on the Raspberry Pi GPIO pins.

    Requires:
        * **RPi.GPIO** (`pip install RPi.GPIO`)
    """

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

        return Response(output={
            'pin': pin,
            'val': val,
            'method': 'write',
        })

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

        return Response(output={
            'pin': pin,
            'val': val,
            'method': 'read',
        })


# vim:sw=4:ts=4:et:

