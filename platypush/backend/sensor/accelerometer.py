from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorAccelerometerBackend(SensorBackend):
    """
    Backend to poll position information from an accelerometer sensor.

    Requires:

        * ``Adafruit_Python_GPIO`` (``pip install Adafruit_Python_GPIO``)
        * The :mod:`platypush.plugins.gpio.sensor.accelerometer` plugin configured
    """

    def get_measurement(self):
        """ get_measurement implementation """
        plugin = get_plugin('gpio.sensor.accelerometer')
        return plugin.get_data().output


# vim:sw=4:ts=4:et:

