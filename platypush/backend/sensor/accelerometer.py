from platypush.backend.sensor import SensorBackend


class SensorAccelerometerBackend(SensorBackend):
    """
    Backend to poll position information from an accelerometer sensor.

    Requires:

        * ``Adafruit_Python_GPIO`` (``pip install Adafruit_Python_GPIO``)
        * The :mod:`platypush.plugins.gpio.sensor.accelerometer` plugin configured
    """

    def __init__(self, **kwargs):
        super().__init__(plugin='gpio.sensor.accelerometer', **kwargs)


# vim:sw=4:ts=4:et:
