import time

from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorDistanceVl53L1XPlugin(GpioSensorPlugin):
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
    def _get_device(self, ranging=1):
        if self._device:
            return self._device

        from VL53L1X import VL53L1X
        self._device = VL53L1X(i2c_bus=self.i2c_bus, i2c_address=self.i2c_address)
        self._device.open()
        self._device.start_ranging(ranging)
        return self._device

    @action
    def get_measurement(self, short=True, medium=False, long=False):
        """
        :param short: Enable short range measurement (default: True)
        :param medium: Enable medium range measurement (default: False)
        :param long: Enable long range measurement (default: False)

        :returns: dict. Example:

        .. code-block:: python

            output = {
                "short": 83,     # Short range measurement in mm
                "medium": 103,   # Medium range measurement
                "long": 43,      # Long range measurement
            }

        """

        range_idx = 0
        range_name = None

        for i, r in enumerate(['short', 'medium', 'long']):
            if eval(r):
                range_idx = i+1
                range_name = r
                break

        assert range_name is not None
        device = self._get_device(ranging=range_idx)
        ret = {}

        try:
            ret[range_name] = device.get_distance()
        except Exception as e:
            self.logger.exception(e)

            try:
                self._device.stop_ranging()
                self._device.close()
            except:
                pass

            self._device = None
            time.sleep(1)

        return ret


# vim:sw=4:ts=4:et:
