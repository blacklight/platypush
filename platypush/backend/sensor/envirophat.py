from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorEnvirophatBackend(SensorBackend):
    """
    Backend to poll analog sensor values from an MCP3008 chipset
    (https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008)

    Requires:

        * ``envirophat`` (``pip install envirophat``)
    """

    def __init__(self, temperature=True, pressure=True, altitude=True, luminosity=True,
                 analog=True, accelerometer=True, magnetometer=True, qnh=1020, **kwargs):
        """
        :param temperature: Enable temperature sensor polling
        :param pressure: Enable pressure sensor polling
        :param altitude: Enable altitude sensor polling
        :param luminosity: Enable luminosity sensor polling
        :param analog: Enable analog sensors polling
        :param accelerometer: Enable accelerometer polling
        :param magnetometer: Enable magnetometer polling
        :param qnh: Base reference for your sea level pressure (for altitude sensor)
        """
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
        sensors = plugin.get_data(qnh=self.qnh).output
        ret = {
            sensor: sensors[sensor]
            for sensor, enabled in self.enabled_sensors.items()
            if enabled and sensor in sensors
        }

        return ret


# vim:sw=4:ts=4:et:
