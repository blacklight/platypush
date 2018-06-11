from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorSerialBackend(SensorBackend):
    def get_measurement(self):
        plugin = get_plugin('serial')
        return plugin.get_data().output


# vim:sw=4:ts=4:et:

