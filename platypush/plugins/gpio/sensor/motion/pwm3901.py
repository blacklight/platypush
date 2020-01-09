import enum
import math
import time

from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class Rotation(enum.IntEnum):
    ROTATE_0 = 0
    ROTATE_90 = 90
    ROTATE_180 = 180
    ROTATE_270 = 270


class SPISlot(enum.Enum):
    FRONT = 'front'
    BACK = 'back'


class GpioSensorMotionPwm3901Plugin(GpioSensorPlugin):
    """
    Plugin to interact with an `PWM3901 <https://github.com/pimoroni/pmw3901-python>`_
    optical flow and motion sensor

    Requires:

        * ``pwm3901`` (``pip install pwm3901``)
    """

    def __init__(self, rotation=Rotation.ROTATE_0.value, spi_slot=SPISlot.FRONT.value, spi_port=0, **kwargs):
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
        super().__init__(**kwargs)

        self.spi_port = spi_port
        self._sensor = None
        self._events_per_sec = {}
        self.x, self.y = (0, 0)

        try:
            if isinstance(rotation, int):
                rotation = [r for r in Rotation if r.value == rotation][0]
            self.rotation = rotation
        except IndexError:
            raise ValueError('{} is not a valid value for rotation - possible values: {}'.format(
                rotation, [r.value for r in Rotation]))

        try:
            if isinstance(spi_slot, str):
                spi_slot = [s for s in SPISlot if s.value == spi_slot][0]

            if spi_slot == SPISlot.FRONT:
                self.spi_slot = BG_CS_FRONT_BCM
            else:
                self.spi_slot = BG_CS_BACK_BCM
        except IndexError:
            raise ValueError('{} is not a valid value for spi_slot - possible values: {}'.format(
                spi_slot, [s.value for s in SPISlot]))

    def _get_sensor(self):
        from pmw3901 import PMW3901

        if not self._sensor:
            self._sensor = PMW3901(spi_port=self.spi_port,
                                   spi_cs=1,
                                   spi_cs_gpio=self.spi_slot)
            self._sensor.set_rotation(self.rotation)

        return self._sensor

    @action
    def get_measurement(self):
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
                time.sleep(0.01)

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


# vim:sw=4:ts=4:et:
