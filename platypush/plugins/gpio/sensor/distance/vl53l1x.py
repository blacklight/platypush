from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorDistanceVl53l1xPlugin(GpioSensorPlugin):
    """
    Plugin to interact with an `VL53L1x <https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html>`_
    laser ranger/distance sensor

    Requires:

        * ``smbus2`` (``pip install smbus2``)
        * ``vl53l1x`` (``pip install vl53l1x``)
    """

    def __init__(self, i2c_bus=1, i2c_address=0x29, **kwargs):
        """
        :param i2c_bus: I2C bus number (default: 1)
        :param i2c_address: I2C address (default: 0x29)
        """

        super().__init__(**kwargs)

        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self._device = None

    # noinspection PyUnresolvedReferences
    def _get_device(self):
        if self._device:
            return self._device

        import VL53L1X
        self._device = VL53L1X(i2c_bus=self.i2c_bus, i2c_address=self.i2c_address)
        return self._device

    @action
    def get_measurement(self, short=True, medium=True, long=True):
        """
        :param short: Enable short range measurement (default: True)
        :param medium: Enable medium range measurement (default: True)
        :param long: Enable long range measurement (default: True)

        :returns: dict. Example::

            output = {
                "short": 83,     # Short range measurement in mm
                "medium": 103,   # Medium range measurement
                "long": 43,      # Long range measurement
            }

        """

        device = self._get_device()
        device.open()
        ret = {}

        for i, r in enumerate(['short', 'medium', 'long']):
            if eval(r):
                device.start_ranging(i+1)
                ret[r] = device.get_distance()
                device.stop_ranging()

        return ret


# vim:sw=4:ts=4:et:
