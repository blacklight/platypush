from platypush.backend.sensor import SensorBackend


class SensorBme280Backend(SensorBackend):
    """
    Backend to poll analog sensor values from a `BME280 <https://shop.pimoroni.com/products/bme280-breakout>`_
    environment sensor

    Requires:

        * ``pimoroni-bme280`` (``pip install pimoroni-bme280``)
    """

    def __init__(self, temperature=True, pressure=True, humidity=True, **kwargs):
        """
        :param temperature: Enable temperature sensor polling
        :param pressure: Enable pressure sensor polling
        :param humidity: Enable humidity sensor polling
        """

        enabled_sensors = {
            'temperature': temperature,
            'pressure': pressure,
            'humidity': humidity,
        }

        super().__init__(plugin='gpio.sensor.bme280', enabled_sensors=enabled_sensors, **kwargs)


# vim:sw=4:ts=4:et:
