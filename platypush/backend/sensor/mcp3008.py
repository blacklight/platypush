from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorMcp3008Backend(SensorBackend):
    """
    Backend to poll analog sensor values from an MCP3008 chipset
    (https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008)

    Requires:

        * ``adafruit-mcp3008`` (``pip install adafruit-mcp3008``)
        * The :mod:`platypush.plugins.gpio.sensor.mcp3008` plugin configured
    """

    def get_measurement(self):
        """ get_measurement implementation """
        plugin = get_plugin('gpio.sensor.mcp3008')
        return plugin.get_data().output


# vim:sw=4:ts=4:et:

