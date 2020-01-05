import enum
import threading
import time

from typing import Dict, List

from platypush.context import get_bus
from platypush.message.event.zeroborg import ZeroborgDriveEvent, ZeroborgStopEvent
from platypush.plugins import Plugin, action


class Direction(enum.Enum):
    DIR_UP = 'up'
    DIR_DOWN = 'down'
    DIR_LEFT = 'left'
    DIR_RIGHT = 'right'


# noinspection PyPep8Naming
class GpioZeroborgPlugin(Plugin):
    """
    ZeroBorg plugin. It allows you to control a ZeroBorg
    (https://www.piborg.org/motor-control-1135/zeroborg) motor controller and
    infrared sensor circuitry for Raspberry Pi

    Triggers:

        * :class:`platypush.message.event.zeroborg.ZeroborgDriveEvent` when motors direction changes
        * :class:`platypush.message.event.zeroborg.ZeroborgStopEvent` upon motors stop

    """

    def __init__(self, directions: Dict[str, List[float]] = None, **kwargs):
        """
        :param directions: Configuration for the motor directions. A direction is basically a configuration of the
            power delivered to each motor to allow whichever object you're controlling (wheels, robotic arms etc.) to
            move in a certain direction. In my experience the ZeroBorg always needs a bit of calibration, depending on
            factory defaults and the mechanical properties of the load it controls.

        Example configuration that I use to control a simple 4WD robot::

            directions = {
                "up": [
                    0.4821428571428572,   # Motor 1 power
                    0.4821428571428572,   # Motor 2 power
                    -0.6707142857142858,  # Motor 3 power
                    -0.6707142857142858   # Motor 4 power
                ],
                "down": [
                    -0.4821428571428572,
                    -0.4821428571428572,
                    0.825,
                    0.825
                ],
                "left": [
                    -0.1392857142857143,
                    -0.1392857142857143,
                    -1.0553571428571429,
                    -1.0553571428571429
                ],
                "right": [
                    1.0017857142857143,
                    1.0017857142857143,
                    0.6214285714285713,
                    0.6214285714285713
                ]
            }

        """

        if directions is None:
            directions = {}

        import platypush.plugins.gpio.zeroborg.lib as ZeroBorg
        super().__init__(**kwargs)

        self.directions = directions
        self._direction = None
        self._drive_thread = None
        self._motors = [0, 0, 0, 0]

        self.zb = ZeroBorg.ZeroBorg()
        self.zb.Init()
        self.zb.SetCommsFailsafe(True)
        self.zb.ResetEpo()

    @staticmethod
    def _get_measurement(plugin, timeout):
        measure_start_time = time.time()
        value = None

        while value is None:
            value = plugin.get_measurement().output
            if time.time() - measure_start_time > timeout:
                return None

        return value

    @action
    def drive(self, direction):
        """
        Drive the motors in a certain direction.
        """

        def _run():
            try:
                while self._direction:
                    try:
                        if self._direction in self.directions:
                            self._motors = self.directions[self._direction]
                        else:
                            self.logger.warning('Invalid direction {}: stopping motors'.format(self._direction))
                    except Exception as e:
                        self.logger.error('Error on _get_direction_from_sensors: {}'.format(str(e)))
                        break

                    for i, power in enumerate(self._motors):
                        method = getattr(self.zb, 'SetMotor{}'.format(i+1))
                        method(power)
            finally:
                self.zb.MotorsOff()
                self.zb.ResetEpo()
                self._drive_thread = None

        self._direction = direction.lower()

        if not self._drive_thread:
            drive_thread = threading.Thread(target=_run)
            drive_thread.start()
            self._drive_thread = drive_thread

        get_bus().post(ZeroborgDriveEvent(direction=self._direction, motors=self.directions[self._direction]))
        return {'status': 'running', 'direction': direction}

    @action
    def stop(self):
        """
        Turns off the motors
        """

        self._direction = None
        if self._drive_thread:
            self._drive_thread.join()

        get_bus().post(ZeroborgStopEvent())
        return {'status': 'stopped'}

    @action
    def status(self) -> dict:
        """
        Get the current direction and motors power. Example response::

            .. code-block:: json

            {
                "status": "running",
                "direction": "up",
                "motors": [1.0, 1.0, -1.0, -1.0]
            }

        """

        return {
            'status': 'running' if self._direction else 'stopped',
            'direction': self._direction,
            'motors': [getattr(self.zb, 'GetMotor{}'.format(i+1))() for i in range(4)],
        }


# vim:sw=4:ts=4:et:
