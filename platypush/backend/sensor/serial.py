import serial

from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorSerialBackend(SensorBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_measurement(self):
        plugin = get_plugin('serial')
        return plugin.get_data().output

    def run(self):
        self.logger.info('Initialized serial backend')
        super().run()


# vim:sw=4:ts=4:et:

