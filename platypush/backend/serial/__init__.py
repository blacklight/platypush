import logging
import serial
import tempfile
import time

from platypush.backend import Backend
from platypush.message.event.serial import SerialDataEvent

class SerialBackend(Backend):
    def __init__(self, device, baud_rate=9600, **kwargs):
        super().__init__(**kwargs)

        self.device = device
        self.baud_rate = baud_rate
        self.serial = None
        self.data = None
        self.tmp_file = tempfile.TemporaryFile()

    def send_message(self, msg):
        pass

    def get_data(self):
        self.tmp_file.seek(0)
        data = self.tmp_file.read()
        self.tmp_file.seek(0)

        return data.decode('utf-8')

    def run(self):
        super().run()

        self.serial = serial.Serial(self.device, self.baud_rate)
        logging.info('Initialized serial backend on device {}'.format(self.device))

        try:
            while not self.should_stop():
                new_data = self.serial.readline().decode('utf-8').strip()
                if self.data is None or self.data != new_data:
                    self.bus.post(SerialDataEvent(data=new_data, device=self.device))

                self.data = new_data

                self.tmp_file.seek(0)
                self.tmp_file.write(self.data.encode('utf-8'))
                self.tmp_file.seek(0)
        finally:
            self.tmp_file.close()


# vim:sw=4:ts=4:et:

