import threading
import time

import RPi.GPIO as gpio

from platypush.message.response import Response
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorDistancePlugin(GpioSensorPlugin):
    def __init__(self, trigger_pin, echo_pin, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self._is_probing = False

        gpio.setmode(gpio.BCM)
        gpio.setup(self.trigger_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)

        self.logger.info('Resetting trigger sensor on GPIO pin {}'.format(self.trigger_pin))
        gpio.output(self.trigger_pin, False)


    def get_measurement(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.trigger_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)

        gpio.output(self.trigger_pin, True)
        time.sleep(0.00001)  # 1 us pulse to trigger echo measurement
        gpio.output(self.trigger_pin, False)
        read_timeout = False

        pulse_start = time.time()
        pulse_on = pulse_start

        while gpio.input(self.echo_pin) == 0:
            pulse_on = time.time()
            if pulse_on - pulse_start > 0.5:
                self.logger.warning('Distance sensor echo timeout: 0')
                read_timeout = True
                break

        pulse_start = pulse_on
        pulse_end = time.time()
        pulse_off = pulse_end

        while gpio.input(self.echo_pin) == 1:
            pulse_off = time.time()
            if pulse_off - pulse_end > 0.5:
                self.logger.warning('Distance sensor echo timeout: 1')
                read_timeout = True
                break

        if read_timeout:
            return None

        pulse_end = pulse_off
        pulse_duration = pulse_end - pulse_start

        # s = vt where v = avg speed of sound
        return round(pulse_duration * 171500.0, 2)


# vim:sw=4:ts=4:et:

