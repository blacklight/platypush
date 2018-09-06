from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorDistanceBackend(SensorBackend):
    """
    Backend to poll a distance sensor.

    Requires:

        * ``RPi.GPIO`` (``pip install RPi.GPIO``)
        * The :mod:`platypush.plugins.gpio.sensor.distance` plugin configured
    """

    def get_measurement(self):
        """ get_measurement implementation """
        plugin = get_plugin('gpio.sensor.distance')
        return {"distance": plugin.get_data().output }


# vim:sw=4:ts=4:et:


