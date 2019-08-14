from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorBme280Plugin(GpioSensorPlugin):
    """
    Plugin to interact with a `BME280 <https://shop.pimoroni.com/products/bme280-breakout>`_ environment sensor for
    temperature, humidity and pressure measurements over I2C interface

    Requires:

        * ``pimoroni-bme280`` (``pip install pimoroni-bme280``)
    """

    def __init__(self, port=1, **kwargs):
        """
        :param port: I2C port. 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        """

        super().__init__(**kwargs)
        self.port = port

    # noinspection PyPackageRequirements
    # noinspection PyUnresolvedReferences
    @action
    def get_measurement(self):
        """
        :returns: dict. Example::

            output = {
                "temperature": 21.0,   # Celsius
                "pressure": 101555.08, # Pascals
                "humidity": 23.543,    # percentage
            }

        """

        from smbus import SMBus
        from bme280 import BME280

        bus = SMBus(self.port)
        device = BME280(i2c_dev=bus)
        return {
            'temperature': device.get_temperature(),
            'pressure': device.get_pressure()*100,
            'humidity': device.get_humidity(),
        }


# vim:sw=4:ts=4:et:
