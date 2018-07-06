import threading
import time

from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorDistancePlugin(GpioSensorPlugin):
    """
    You can use this plugin to interact with a distance sensor on your Raspberry
    Pi (tested with a HC-SR04 ultrasound sensor).

    Requires:

        * ``RPi.GPIO`` (``pip install RPi.GPIO``)
    """

    def __init__(self, trigger_pin, echo_pin, *args, **kwargs):
        """
        :param trigger_pin: GPIO PIN where you connected your sensor trigger PIN (the one that triggers the sensor to perform a measurement).
        :type trigger_pin: int

        :param echo_pin: GPIO PIN where you connected your sensor echo PIN (the one that will listen for the signal to bounce back and therefore trigger the distance calculation).
        :type echo_pin: int
        """

        import RPi.GPIO as gpio
        super().__init__(*args, **kwargs)

        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self._is_probing = False

        gpio.setmode(gpio.BCM)
        gpio.setup(self.trigger_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)

        self.logger.info('Resetting trigger sensor on GPIO pin {}'.format(self.trigger_pin))
        gpio.output(self.trigger_pin, False)


    @action
    def get_measurement(self):
        """
        Extends :func:`.GpioSensorPlugin.get_measurement`

        :returns: Distance measurement as a scalar (in mm):
        """

        import RPi.GPIO as gpio
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

