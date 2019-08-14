from platypush.backend.sensor import SensorBackend


class SensorDistanceVl53l1xBackend(SensorBackend):
    """
    Backend to poll an `VL53L1x <https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html>`_
    laser ranger/distance sensor

    Requires:

        * ``smbus2`` (``pip install smbus2``)
        * ``vl53l1x`` (``pip install vl53l1x``)
    """

    def __init__(self, short=True, medium=True, long=True, **kwargs):
        """
        :param short: Enable short range measurement (default: True)
        :param medium: Enable medium range measurement (default: True)
        :param long: Enable long range measurement (default: True)
        """
        enabled_sensors = {
            'short': short,
            'medium': medium,
            'long': long,
        }

        super().__init__(plugin='gpio.sensor.distance.vl53l1x', enabled_sensors=enabled_sensors, **kwargs)


# vim:sw=4:ts=4:et:
