from platypush.backend.sensor import SensorBackend


class SensorDistanceVl53L1XBackend(SensorBackend):
    """
    Backend to poll an `VL53L1x <https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html>`_
    laser ranger/distance sensor

    Requires:

        * ``smbus2`` (``pip install smbus2``)
        * ``vl53l1x`` (``pip install vl53l1x``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def __init__(self, short=True, medium=False, long=False, **kwargs):
        """
        :param short: Enable short range measurement (default: True)
        :param medium: Enable medium range measurement (default: False)
        :param long: Enable long range measurement (default: False)
        """
        enabled_sensors = {
            'short': short,
            'medium': medium,
            'long': long,
        }

        super().__init__(plugin='gpio.sensor.distance.vl53l1x', enabled_sensors=enabled_sensors, **kwargs)


# vim:sw=4:ts=4:et:
