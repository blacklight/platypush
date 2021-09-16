from platypush.backend.sensor import SensorBackend


class SensorDhtBackend(SensorBackend):
    """
    Backend to poll a DHT11/DHT22/AM2302 temperature/humidity sensor.

    Requires:

        * ``Adafruit_Python_DHT`` (``pip install git+https://github.com/adafruit/Adafruit_Python_DHT.git``)
        * The ``gpio.sensor.dht`` plugin configured and enabled.

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def __init__(self, temperature: bool = True, humidity: bool = True, **kwargs):
        """
        :param temperature: Enable temperature sensor poll.
        :param humidity: Enable humidity sensor poll.
        """

        enabled_sensors = {
            'humidity': humidity,
            'temperature': temperature,
        }

        super().__init__(plugin='gpio.sensor.dht', enabled_sensors=enabled_sensors, **kwargs)


# vim:sw=4:ts=4:et:
