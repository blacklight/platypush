from contextlib import contextmanager
from threading import RLock
from typing import List, Mapping
from typing_extensions import override

from platypush.entities.devices import Device
from platypush.entities.distance import DistanceSensor
from platypush.plugins.sensor import SensorPlugin


# pylint: disable=too-many-ancestors
class SensorDistanceVl53l1xPlugin(SensorPlugin):
    """
    Plugin to interact with an `VL53L1x
    <https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html>`_
    laser ranger/distance sensor

    Requires:

        * ``smbus2`` (``pip install smbus2``)
        * ``vl53l1x`` (``pip install vl53l1x``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    def __init__(self, i2c_bus=1, i2c_address=0x29, poll_interval=3, **kwargs):
        """
        :param i2c_bus: I2C bus number (default: 1)
        :param i2c_address: I2C address (default: 0x29)
        :param poll_interval: How often the integration should poll for new
            measurements (default: 3 seconds).
        """

        super().__init__(poll_interval=poll_interval, **kwargs)

        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self._device = None
        self._device_lock = RLock()
        self._last_data = {}

    @contextmanager
    def _get_device(self, ranging=1):
        from VL53L1X import VL53L1X  # type: ignore

        with self._device_lock:
            if self._device:
                yield self._device

            self._device = VL53L1X(i2c_bus=self.i2c_bus, i2c_address=self.i2c_address)

            try:
                self._device.open()
                self._device.start_ranging(ranging)
                yield self._device
            finally:
                try:
                    self._device.stop_ranging()
                except Exception:
                    pass

                self._device.close()
                self._device = None

    @override
    def get_measurement(self, *_, short=True, medium=True, long=True, **__):
        """
        :param short: Enable short range measurement (default: True)
        :param medium: Enable medium range measurement (default: True)
        :param long: Enable long range measurement (default: True)

        :returns: dict. Example:

        .. code-block:: python

            output = {
                "short": 83,     # Short range measurement in mm
                "medium": 103,   # Medium range measurement in mm
                "long": 200,     # Long range measurement
            }

        """

        ret = {}
        range_idx = 0
        range_name = None
        range_conf = {
            'short': short,
            'medium': medium,
            'long': long,
        }

        for i, (key, enabled) in enumerate(range_conf.items()):
            if not enabled:
                continue

            range_idx = i + 1
            range_name = key

            with self._get_device(ranging=range_idx) as device:
                try:
                    ret[range_name] = device.get_distance()
                except Exception as e:
                    self.logger.exception(e)
                    self.wait_stop(1)

        return ret

    @override
    def transform_entities(self, entities: Mapping[str, int]) -> List[Device]:
        return [
            Device(
                id='vl53l1x',
                name='VL53L1X Distance Sensor',
                children=[
                    DistanceSensor(
                        id=f'vl53l1x:{key}',
                        name=f'{key} distance',
                        value=value,
                        unit='mm',
                    )
                    for key, value in entities.items()
                ],
            )
        ]


# vim:sw=4:ts=4:et:
