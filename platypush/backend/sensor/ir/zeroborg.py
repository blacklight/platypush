import logging
import time

import platypush.plugins.gpio.zeroborg.lib as ZeroBorg

from platypush.backend import Backend
from platypush.message.event.sensor.ir import IrKeyUpEvent, IrKeyDownEvent

class SensorIrZeroborgBackend(Backend):
    last_message =None
    last_message_timestamp = None

    def __init__(self, no_message_timeout=0.37, **kwargs):
        super().__init__(**kwargs)
        self.no_message_timeout = no_message_timeout
        self.zb = ZeroBorg.ZeroBorg()
        self.zb.Init()
        logging.info('Initialized Zeroborg infrared sensor backend')


    def send_message(self, message):
        pass


    def run(self):
        super().run()

        while True:
            try:
                self.zb.GetIrMessage()
                if self.zb.HasNewIrMessage():
                    message = self.zb.GetIrMessage()
                    if message != self.last_message:
                        logging.info('Received key down event on the IR sensor: {}'.format(message))
                        self.bus.post(IrKeyDownEvent(message=message))

                    self.last_message = message
                    self.last_message_timestamp = time.time()
            except OSError as e:
                logging.warning('Failed reading IR sensor status')

            if self.last_message_timestamp and \
                    time.time() - self.last_message_timestamp > self.no_message_timeout:
                logging.info('Received key up event on the IR sensor')
                self.bus.post(IrKeyUpEvent(message=self.last_message))

                self.last_message = None
                self.last_message_timestamp = None


# vim:sw=4:ts=4:et:

