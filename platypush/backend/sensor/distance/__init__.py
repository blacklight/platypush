from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorDistanceBackend(SensorBackend):
    """
    Backend to poll a distance sensor.

    Requires:

        * ``RPi.GPIO`` (``pip install RPi.GPIO``)
        * The :mod:`platypush.plugins.gpio.sensor.distance` plugin configured

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def get_measurement(self):
        """ get_measurement implementation """
        plugin = get_plugin('gpio.sensor.distance')
        return {"distance": plugin.get_data().output }


# vim:sw=4:ts=4:et:


