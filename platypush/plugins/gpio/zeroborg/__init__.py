import enum
import logging
import threading
import time

from platypush.message.response import Response
from platypush.plugins import Plugin
from platypush.context import get_plugin
from platypush.config import Config


class Direction(enum.Enum):
    DIR_UP = 'up'
    DIR_DOWN = 'down'
    DIR_LEFT = 'left'
    DIR_RIGHT = 'right'
    DIR_AUTO = 'auto'


class GpioZeroborgPlugin(Plugin):
    _drive_thread = None
    _can_run = False
    _direction = None
    _power_offsets = {
        Direction.DIR_LEFT: {
            Direction.DIR_UP: 0.242,
            Direction.DIR_DOWN: 0.285,
        },

        Direction.DIR_RIGHT: {
            Direction.DIR_UP: 0,
            Direction.DIR_DOWN: 0.242,
        },
    }


    def __init__(self, v_in=8.4, v_out=6.0):
        import platypush.plugins.gpio.zeroborg.lib as ZeroBorg

        self.v_in = v_in
        self.v_out = v_out
        self.max_power = v_out / float(v_in)
        self.auto_mode = False

        self.zb = ZeroBorg.ZeroBorg()
        self.zb.Init()
        self.zb.SetCommsFailsafe(True)
        self.zb.ResetEpo()


    def get_distance(self):
        distance_sensor = get_plugin('gpio.sensor.distance')
        if not distance_sensor:
            raise RuntimeError('No gpio.sensor.distance configuration found')

        return distance_sensor.get_distance()


    def drive(self, direction):
        self._can_run = True
        self._direction = direction.lower()
        logging.info('Received ZeroBorg drive command: {}'.format(direction))

        def _run():
            while self._can_run and self._direction:
                left = 0.0
                right = 0.0

                if self._direction == Direction.DIR_AUTO.value:
                    self.auto_mode = True

                if self.auto_mode:
                    distance = None
                    while distance is None:
                        distance = self.get_distance()

                    print(distance)
                    if distance > 250.0:  # distance in mm
                        self._direction = Direction.DIR_UP.value
                    else:
                        self._direction = Direction.DIR_LEFT.value

                    time.sleep(0.1)

                if self._direction == Direction.DIR_UP.value:
                    left = 1.0 + self._power_offsets[Direction.DIR_LEFT][Direction.DIR_UP]
                    right = 1.0 + self._power_offsets[Direction.DIR_RIGHT][Direction.DIR_UP]
                elif self._direction == Direction.DIR_DOWN.value:
                    left = -1.0 - self._power_offsets[Direction.DIR_LEFT][Direction.DIR_DOWN]
                    right = -1.0 - self._power_offsets[Direction.DIR_RIGHT][Direction.DIR_DOWN]
                elif self._direction == Direction.DIR_LEFT.value:
                    left = 2.0 + self._power_offsets[Direction.DIR_LEFT][Direction.DIR_UP]
                    right = -1.25 - self._power_offsets[Direction.DIR_RIGHT][Direction.DIR_DOWN]
                elif self._direction == Direction.DIR_RIGHT.value:
                    left = -1.25 - self._power_offsets[Direction.DIR_LEFT][Direction.DIR_DOWN]
                    right = 2.0 + self._power_offsets[Direction.DIR_RIGHT][Direction.DIR_UP]
                elif self._direction is not None:
                    logging.warning('Invalid direction: {}'.format(direction))
                    self.stop()

                self.zb.SetMotor1(left * self.max_power)
                self.zb.SetMotor2(left * self.max_power)
                self.zb.SetMotor3(-right * self.max_power)
                self.zb.SetMotor4(-right * self.max_power)

            self.auto_mode = False


        self._drive_thread = threading.Thread(target=_run)
        self._drive_thread.start()

        return Response(output={'status': 'running', 'direction': direction})


    def stop(self):
        self._can_run = False
        if self._drive_thread and threading.get_ident() != self._drive_thread.ident:
            self._drive_thread.join()

        self.zb.MotorsOff()
        self.zb.ResetEpo()

        return Response(output={'status':'stopped'})


# vim:sw=4:ts=4:et:

