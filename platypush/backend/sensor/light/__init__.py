import logging
import time

import RPi.GPIO as gpio

from platypush.backend import Backend
from platypush.message.event.sensor.light import LightOnEvent, LightOffEvent


class SensorLightBackend(Backend):
    state = None

    def __init__(self, pin, threshold=0.5, poll_seconds=0.5, **kwargs):
        super().__init__(**kwargs)

        self.pin = pin
        self.threshold = threshold
        self.poll_seconds = poll_seconds

    def send_message(self, msg):
        pass

    def get_state(self):
        return self.state

    def run(self):
        super().run()

        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin, gpio.IN)
        logging.info('Initialized light sensor backend on pin {}'.format(self.pin))

        try:
            while not self.should_stop():
                value = float(gpio.input(self.pin))
                new_state = True if value >= self.threshold else False

                if self.state is not None and new_state != self.state:
                    if new_state is True:
                        self.bus.post(LightOnEvent())
                    else:
                        self.bus.post(LightOffEvent())

                self.state = new_state
                time.sleep(self.poll_seconds)
        finally:
            gpio.cleanup()


# vim:sw=4:ts=4:et:

