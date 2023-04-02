import enum
import math
import time
from typing import Dict, List
from typing_extensions import override

from platypush.common.sensors import Numeric
from platypush.entities.devices import Device
from platypush.entities.distance import DistanceSensor
from platypush.entities.sensors import NumericSensor, RawSensor
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


class Rotation(enum.IntEnum):
    """
    Enumerates the possible rotations of the sensor.
    """

    ROTATE_0 = 0
    ROTATE_90 = 90
    ROTATE_180 = 180
    ROTATE_270 = 270


class SPISlot(enum.Enum):
    """
    Enumeration for the possible SPI slot positions of the sensor on the
    Breakout Garden (front or back).
    """

    FRONT = 'front'
    BACK = 'back'


# pylint: disable=too-many-ancestors
class SensorPmw3901Plugin(SensorPlugin):
    """
    Plugin to interact with an `PMW3901 <https://github.com/pimoroni/pmw3901-python>`_
    optical flow and motion sensor

    Requires:

        * ``pmw3901`` (``pip install pmw3901``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    def __init__(
        self,
        rotation=Rotation.ROTATE_0.value,
        spi_slot=SPISlot.FRONT.value,
        spi_port=0,
        poll_interval=0.01,
        **kwargs,
    ):
        """
        :param rotation: Rotation angle for the captured optical flow. Possible options: 0, 90, 180, 270 (default: 0)
        :type rotation: int

        :param spi_slot: SPI slot where the sensor is connected if you're using a Breakout Garden interface.
            Possible options: 'front', 'back' (default: 'front')
        :type spi_slot: str

        :param spi_port: SPI port (default: 0)
        :type spi_slot: int
        """
        from pmw3901 import BG_CS_FRONT_BCM, BG_CS_BACK_BCM

        super().__init__(poll_interval=poll_interval, **kwargs)

        self.spi_port = spi_port
        self._sensor = None
        self._events_per_sec = {}
        self.x, self.y = (0, 0)

        try:
            if isinstance(rotation, int):
                rotation = [r for r in Rotation if r.value == rotation][0]
            self.rotation = rotation
        except IndexError as e:
            raise AssertionError(
                f'{rotation} is not a valid value for rotation - '
                f'possible values: {[r.value for r in Rotation]}'
            ) from e

        try:
            if isinstance(spi_slot, str):
                spi_slot = [s for s in SPISlot if s.value == spi_slot][0]

            if spi_slot == SPISlot.FRONT:
                self.spi_slot = BG_CS_FRONT_BCM
            else:
                self.spi_slot = BG_CS_BACK_BCM
        except IndexError as e:
            raise AssertionError(
                f'{spi_slot} is not a valid value for spi_slot - '
                f'possible values: {[s.value for s in SPISlot]}'
            ) from e

    def _get_sensor(self):
        from pmw3901 import PMW3901

        if not self._sensor:
            self._sensor = PMW3901(
                spi_port=self.spi_port, spi_cs=1, spi_cs_gpio=self.spi_slot
            )
            self._sensor.set_rotation(self.rotation)

        return self._sensor

    @override
    @action
    def get_measurement(self, *_, **__):
        """
        :returns: dict. Example:

        .. code-block:: python

           output = {
               "motion_x": 3,   # Detected motion vector X-coord
               "motion_y": 4,   # Detected motion vector Y-coord
               "motion_mod": 5  # Detected motion vector module
               "motion_events_per_sec": 7  # Number of motion events detected in the last second
           }

        """

        sensor = self._get_sensor()

        while True:
            try:
                x, y = sensor.get_motion()
                break
            except RuntimeError:
                self.wait_stop(0.01)

        secs = int(time.time())
        if (x, y) != (self.x, self.y):
            (self.x, self.y) = (x, y)

            if secs not in self._events_per_sec:
                self._events_per_sec = {secs: 1}
            else:
                self._events_per_sec[secs] += 1

        return {
            'motion_x': x,
            'motion_y': y,
            'motion_mod': math.sqrt(x * x + y * y),
            'motion_events_per_sec': self._events_per_sec.get(secs, 0),
        }

    @override
    def transform_entities(self, entities: Dict[str, Numeric]) -> List[Device]:
        return [
            Device(
                id='pmw3901',
                name='PMW3901',
                children=[
                    RawSensor(
                        id='pmw3901:motion',
                        name='motion',
                        description='Motion vector',
                        value=[entities['motion_x'], entities['motion_y']],
                        is_json=True,
                    ),
                    DistanceSensor(
                        id='pmw3901:module',
                        name='module',
                        description='Motion vector module',
                        value=entities['motion_mod'],
                    ),
                    NumericSensor(
                        id='pmw3901:rate',
                        name='rate',
                        description='Events per second',
                        value=entities['motion_events_per_sec'],
                    ),
                ],
            )
        ]


# vim:sw=4:ts=4:et:
