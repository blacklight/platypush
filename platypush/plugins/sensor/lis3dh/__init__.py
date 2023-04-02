from typing import Any, Dict, List
from typing_extensions import override

from platypush.entities.acceleration import Accelerometer
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


# pylint: disable=too-many-ancestors
class SensorLis3dhPlugin(SensorPlugin):
    """
    Plugin to interact with an `Adafruit LIS3DH accelerometer
    <https://www.adafruit.com/product/2809>`_ and get X,Y,Z measurement. Tested
    with a Raspberry Pi over I2C connection.

    Requires:

        * ``Adafruit-GPIO`` (``pip install Adafruit-GPIO``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    def __init__(self, g=4, precision=None, poll_interval=1, **kwargs):
        """
        Only LIS3DH in I2C mode is currently supported: https://learn.adafruit.com/assets/59080.

        :param g: Accelerometer range as a multiple of G - can be 2G, 4G, 8G or 16G
        :type g: int

        :param precision: If set, the position values will be rounded to the specified number of decimal digits
            (default: no rounding)
        :type precision: int
        """

        from .lib.LIS3DH import LIS3DH

        super().__init__(poll_interval=poll_interval, **kwargs)

        if g == 2:
            self.g = LIS3DH.RANGE_2G
        elif g == 4:
            self.g = LIS3DH.RANGE_4G
        elif g == 8:
            self.g = LIS3DH.RANGE_8G
        elif g == 16:
            self.g = LIS3DH.RANGE_16G
        else:
            raise RuntimeError(f'Invalid G range: {g}')

        self.precision = precision
        self.sensor = LIS3DH()
        self.sensor.setRange(self.g)

    @override
    @action
    def get_measurement(self, *_, **__):
        """
        :returns: The sensor's current position as a dictionary with the three components (x,y,z) in degrees, each
            between -90 and 90
        """

        values = [
            (pos * 100 if self.precision is None else round(pos * 100, self.precision))
            for pos in (self.sensor.getX(), self.sensor.getY(), self.sensor.getZ())
        ]

        return {
            'name': 'position',
            'value': {'x': values[0], 'y': values[1], 'z': values[2]},
        }

    @override
    def transform_entities(self, entities: Dict[str, Any]) -> List[Accelerometer]:
        return Accelerometer(
            id='lis3dh',
            name='LIS3DH Accelerometer',
            value=entities['value'],
        )


# vim:sw=4:ts=4:et:
