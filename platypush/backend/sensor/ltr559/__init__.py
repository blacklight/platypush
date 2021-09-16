from platypush.backend.sensor import SensorBackend


class SensorLtr559Backend(SensorBackend):
    """
    Backend to poll an `LTR559 <https://shop.pimoroni.com/products/ltr-559-light-proximity-sensor-breakout>`_
    light/proximity sensor

    Requires:

        * ``ltr559`` (``pip install ltr559``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def __init__(self, light=True, proximity=True, **kwargs):
        """
        :param light: Enable light sensor
        :param proximity: Enable proximity sensor
        """

        enabled_sensors = {
            'light': light,
            'proximity': proximity,
        }

        super().__init__(plugin='gpio.sensor.ltr559', enabled_sensors=enabled_sensors, **kwargs)


# vim:sw=4:ts=4:et:
