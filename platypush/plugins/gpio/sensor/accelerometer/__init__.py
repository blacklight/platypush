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

    def __init__(self, g=4, precision=None, *args, **kwargs):
        """
        Only LIS3DH in I2C mode is currently supported: https://learn.adafruit.com/assets/59080.

        :param g: Accelerometer range as a multiple of G - can be 2G, 4G, 8G or 16G
        :type g: int

        :param precision: If set, the position values will be rounded to the specified number of decimal digits
            (default: no rounding)
        :type precision: int
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

        self.precision = precision
        self.sensor = LIS3DH()
        self.sensor.setRange(self.g)

    @action
    def get_measurement(self):
        """
        Extends :func:`.GpioSensorPlugin.get_measurement`

        :returns: The sensor's current position as a dictionary with the three components (x,y,z) in degrees, each
            between -90 and 90
        """

        values = [
            (pos*100 if self.precision is None else round(pos*100, self.precision))
            for pos in (self.sensor.getX(), self.sensor.getY(), self.sensor.getZ())
        ]

        return {
            'name': 'position',
            'value': {
                'x': values[0], 'y': values[1], 'z': values[2]
            }
        }


# vim:sw=4:ts=4:et:
