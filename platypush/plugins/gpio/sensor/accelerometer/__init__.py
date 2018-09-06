import threading
import time

from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorAccelerometerPlugin(GpioSensorPlugin):
    """
    Plugin to interact with an accelerometer sensor and get X,Y,Z position.
    Tested with Adafruit LIS3DH accelerometer (https://www.adafruit.com/product/2809)
    with Raspberry Pi over I2C connection.

    Requires:

        * ``Adafruit_Python_GPIO`` (``pip install Adafruit_Python_GPIO``)
    """

    def __init__(self, g=4, *args, **kwargs):
        """
        Only LIS3DH in I2C mode is currently supported: https://learn.adafruit.com/assets/59080.

        :param g: Accelerometer range as a multiple of G - can be 2G, 4G, 8G or 16G
        :type g: int
        """

        super().__init__(*args, **kwargs)
        from platypush.plugins.gpio.sensor.accelerometer.lib.LIS3DH import LIS3DH

        if g == 2:
            self.g = LIS3DH.RANGE_2G
        elif g == 4:
            self.g = LIS3DH.RANGE_4G
        elif g == 8:
            self.g = LIS3DH.RANGE_8G
        elif g == 16:
            self.g = LIS3DH.RANGE_16G
        else:
            raise RuntimeError('Invalid G range: {}'.format(g))

        self.sensor = LIS3DH()
        self.sensor.setRange(self.g)


    @action
    def get_measurement(self):
        """
        Extends :func:`.GpioSensorPlugin.get_measurement`

        :returns: The sensor's current position as a list with three elements (x,y,z)
        """

        return [self.sensor.getX(), self.sensor.getY(), self.sensor.getZ()]


# vim:sw=4:ts=4:et:

