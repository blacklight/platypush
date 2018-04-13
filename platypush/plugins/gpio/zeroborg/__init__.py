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
    DIR_AUTO_TOGGLE = 'auto_toggle'


class GpioZeroborgPlugin(Plugin):
    _drive_thread = None
    _can_run = False
    _direction = None


    def __init__(self, directions = {}):
        import platypush.plugins.gpio.zeroborg.lib as ZeroBorg

        self.directions = directions
        self.auto_mode = False
        self._direction = None

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
        prev_direction = self._direction

        self._can_run = True
        self._direction = direction.lower()
        logging.info('Received ZeroBorg drive command: {}'.format(direction))

        def _run():
            while self._can_run and self._direction:
                left = 0.0
                right = 0.0

                if self._direction == Direction.DIR_AUTO_TOGGLE.value:
                    if self.auto_mode:
                        self._direction = None
                        self.auto_mode = False
                    else:
                        self._direction = Direction.DIR_AUTO
                        self.auto_mode = True

                if self._direction == Direction.DIR_AUTO.value:
                    self.auto_mode = True

                if self.auto_mode:
                    distance = None
                    last_recorded_distance_timestamp = None
                    distance_record_timeout = 2.0

                    while distance is None:
                        distance = self.get_distance()
                        logging.info('Closest obstacle distance: {} mm'.format(distance))

                        if last_recorded_distance_timestamp and \
                                time.time() - last_recorded_distance_timestamp > distance_record_timeout:
                            # Stop the motors if we have been unable
                            # to access the distance sensor data
                            self._direction = None
                            break

                    last_recorded_distance_timestamp = time.time()

                    if distance > 400.0:  # distance in mm
                        self._direction = Direction.DIR_UP.value
                    else:
                        logging.info('Physical obstacle detected at {} mm'.
                                     format(distance))
                        self._direction = Direction.DIR_LEFT.value

                    time.sleep(0.1)

                motor_1_power = motor_2_power = motor_3_power = motor_4_power = 0.0
                if self._direction in self.directions:
                    motor_1_power = self.directions[self._direction]['motor_1_power']
                    motor_2_power = self.directions[self._direction]['motor_2_power']
                    motor_3_power = self.directions[self._direction]['motor_3_power']
                    motor_4_power = self.directions[self._direction]['motor_4_power']
                elif self._direction:
                    logging.warning('Invalid direction {}, stopping motors'.format(self._direction))

                self.zb.SetMotor1(motor_1_power)
                self.zb.SetMotor2(motor_2_power)
                self.zb.SetMotor3(motor_3_power)
                self.zb.SetMotor4(motor_4_power)

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

