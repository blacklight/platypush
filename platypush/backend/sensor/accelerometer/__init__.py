from platypush.backend.sensor import SensorBackend


class SensorAccelerometerBackend(SensorBackend):
    """
    Backend to poll position information from an accelerometer sensor.

    Requires:

        * ``Adafruit-GPIO`` (``pip install Adafruit-GPIO``)
        * The :mod:`platypush.plugins.gpio.sensor.accelerometer` plugin configured

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def __init__(self, **kwargs):
        super().__init__(plugin='gpio.sensor.accelerometer', **kwargs)


# vim:sw=4:ts=4:et:
