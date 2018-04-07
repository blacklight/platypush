import logging
import serial
import time

from platypush.backend import Backend
from platypush.message.event.serial import SerialDataEvent


class SerialBackend(Backend):
    state = None

    def __init__(self, device, baud_rate=9600, **kwargs):
        super().__init__(**kwargs)

        self.device = device
        self.baud_rate = baud_rate
        self.serial = None

    def send_message(self, msg):
        pass

    def get_state(self):
        return self.state

    def run(self):
        super().run()

        self.serial = serial.Serial(self.device, self.baud_rate)
        prev_value = None
        logging.info('Initialized serial backend on device {}'.format(self.device))

        while not self.should_stop():
            value = self.serial.readline().decode('utf-8').strip()
            if prev_value is None or value != prev_value:
                self.bus.post(SerialDataEvent(data=value, device=self.device))

            prev_value = value


# vim:sw=4:ts=4:et:

