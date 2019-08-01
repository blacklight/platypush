from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorEnvirophatBackend(SensorBackend):
    """
    Backend to poll analog sensor values from an MCP3008 chipset
    (https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008)

    Requires:

        * ``adafruit-mcp3008`` (``pip install adafruit-mcp3008``)
        * The :mod:`platypush.plugins.gpio.sensor.mcp3008` plugin configured
    """

    def __init__(self, temperature=True, pressure=True, altitude=True, luminosity=True,
                 analog=True, accelerometer=True, magnetometer=True, qnh=1020, **kwargs):
        super().__init__(self, **kwargs)

        self.qnh = qnh
        self.enabled_sensors = {
            'temperature': temperature,
            'pressure': pressure,
            'altitude': altitude,
            'luminosity': luminosity,
            'analog': analog,
            'accelerometer': accelerometer,
            'magnetometer': magnetometer,
        }

    def get_measurement(self):
        plugin = get_plugin('gpio.sensor.envirophat')
        return plugin.get_data(qnh=self.qnh).output


# vim:sw=4:ts=4:et:
