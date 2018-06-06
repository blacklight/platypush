import threading
import time

import RPi.GPIO as gpio

from platypush.message.response import Response
from platypush.plugins import Plugin


class GpioPlugin(Plugin):
    def write(self, pin, val):
        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.OUT)
        gpio.output(pin, val)

        return Response(output={
            'pin': pin,
            'val': val,
            'method': 'write',
        })

    def read(self, pin, val):
        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.IN)
        val = gpio.input(pin)

        return Response(output={
            'pin': pin,
            'val': val,
            'method': 'read',
        })


# vim:sw=4:ts=4:et:

