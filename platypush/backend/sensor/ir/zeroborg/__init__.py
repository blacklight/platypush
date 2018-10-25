import time

import platypush.plugins.gpio.zeroborg.lib as ZeroBorg

from platypush.backend import Backend
from platypush.message.event.sensor.ir import IrKeyUpEvent, IrKeyDownEvent


class SensorIrZeroborgBackend(Backend):
    """
    This backend will read for events on the infrared sensor of a ZeroBorg
    (https://www.piborg.org/motor-control-1135/zeroborg) circuitry for
    Raspberry Pi. You can see the codes associated to an IR event from any
    remote by running the scan utility::

        python -m platypush.backend.sensor.ir.zeroborg.scan

    Triggers:

        * :class:`platypush.message.event.sensor.ir.IrKeyDownEvent` when a key is pressed
        * :class:`platypush.message.event.sensor.ir.IrKeyUpEvent` when a key is released
    """

    last_message =None
    last_message_timestamp = None

    def __init__(self, no_message_timeout=0.37, **kwargs):
        super().__init__(**kwargs)
        self.no_message_timeout = no_message_timeout
        self.zb = ZeroBorg.ZeroBorg()
        self.zb.Init()
        self.logger.info('Initialized Zeroborg infrared sensor backend')


    def run(self):
        super().run()

        while True:
            try:
                self.zb.GetIrMessage()
                if self.zb.HasNewIrMessage():
                    message = self.zb.GetIrMessage()
                    if message != self.last_message:
                        self.logger.info('Received key down event on the IR sensor: {}'.format(message))
                        self.bus.post(IrKeyDownEvent(message=message))

                    self.last_message = message
                    self.last_message_timestamp = time.time()
            except OSError as e:
                self.logger.warning('Failed reading IR sensor status')

            if self.last_message_timestamp and \
                    time.time() - self.last_message_timestamp > self.no_message_timeout:
                self.logger.info('Received key up event on the IR sensor')
                self.bus.post(IrKeyUpEvent(message=self.last_message))

                self.last_message = None
                self.last_message_timestamp = None


# vim:sw=4:ts=4:et:

