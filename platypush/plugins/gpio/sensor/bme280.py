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
        self._bus = None
        self._device = None

    # noinspection PyPackageRequirements
    # noinspection PyUnresolvedReferences
    def _get_device(self):
        if self._device:
            return self._device

        from smbus import SMBus
        from bme280 import BME280

        self._bus = SMBus(self.port)
        self._device = BME280(i2c_dev=self._bus)
        return self._device

    @action
    def get_measurement(self):
        """
        :returns: dict. Example:

        .. code-block:: python

           output = {
               "temperature": 21.0,   # Celsius
               "pressure": 101555.08, # Pascals
               "humidity": 23.543,    # percentage
               "altitude": 15.703     # meters
           }

        """

        device = self._get_device()
        return {
            'temperature': device.get_temperature(),
            'pressure': device.get_pressure()*100,
            'humidity': device.get_humidity(),
            'altitude': device.get_altitude(),
        }


# vim:sw=4:ts=4:et:
