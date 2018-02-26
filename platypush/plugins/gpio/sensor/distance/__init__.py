import logging
import threading
import time

import RPi.GPIO as gpio

from platypush.message.response import Response
from platypush.plugins import Plugin


class GpioSensorDistancePlugin(Plugin):
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.measured_distance_mm = None
        self._is_probing = False

        gpio.setmode(gpio.BCM)
        gpio.setup(self.trigger_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)

        logging.info('Resetting trigger sensor on GPIO pin {}'.format(self.trigger_pin))
        gpio.output(self.trigger_pin, False)
        time.sleep(1)


    def start(self):
        self._is_probing = True
        logging.info('Received distance sensor start command')

        def _run():
            gpio.setmode(gpio.BCM)
            gpio.setup(self.trigger_pin, gpio.OUT)
            gpio.setup(self.echo_pin, gpio.IN)

            while self._is_probing:
                gpio.output(self.trigger_pin, True)
                time.sleep(0.00001)  # 1 us pulse to trigger echo measurement
                gpio.output(self.trigger_pin, False)
                read_timeout = False

                pulse_start = time.time()
                pulse_on = pulse_start

                while gpio.input(self.echo_pin) == 0:
                    pulse_on = time.time()
                    if pulse_on - pulse_start > 0.5:
                        logging.warning('Distance sensor echo timeout: 0')
                        read_timeout = True
                        break

                pulse_start = pulse_on
                pulse_end = time.time()
                pulse_off = pulse_end

                while gpio.input(self.echo_pin) == 1:
                    pulse_off = time.time()
                    if pulse_off - pulse_end > 0.5:
                        logging.warning('Distance sensor echo timeout: 1')
                        read_timeout = True
                        break

                if read_timeout:
                    continue

                pulse_end = pulse_off
                pulse_duration = pulse_end - pulse_start

                # s = vt where v = avg speed of sound
                self.measured_distance_mm = round(pulse_duration * 171500.0, 2)

                gpio.output(self.trigger_pin, False)
                time.sleep(0.1)

            gpio.cleanup()
            self.measured_distance_mm = None

        self._probe_thread = threading.Thread(target=_run)
        self._probe_thread.start()

        return Response(output={'status': 'probing'})


    def get_distance(self):
        return self.measured_distance_mm


    def stop(self):
        self._is_probing = False
        self.measured_distance_mm = None

        if self._probe_thread and threading.get_ident() != self._probe_thread.ident:
            self._probe_thread.join()

        return Response(output={'status':'stopped'})


# vim:sw=4:ts=4:et:

