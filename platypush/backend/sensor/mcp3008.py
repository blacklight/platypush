from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorMcp3008Backend(SensorBackend):
    def get_measurement(self):
        plugin = get_plugin('gpio.sensor.mcp3008')
        return plugin.get_data().output


# vim:sw=4:ts=4:et:

