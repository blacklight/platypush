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


    def _get_measurement(self, plugin, timeout):
        measure_start_time = time.time()
        value = None

        while value is None:
            value = plugin.get_measurement()
            if time.time() - measure_start_time > timeout:
                return None

        return value

    def _get_direction_from_sensors(self):
        if Direction.DIR_AUTO.value not in self.directions:
            raise RuntimeError("Can't start auto pilot: " +
                               "no sensor configured in gpio.zeroborg.directions.auto")

        direction = None

        for sensor in self.directions[Direction.DIR_AUTO.value]['sensors']:
            plugin = get_plugin(sensor['plugin'])
            if not sensor:
                raise RuntimeError('No such sensor: ' + sensor['plugin'])

            value = self._get_measurement(plugin=plugin, timeout=sensor['timeout'])
            threshold = sensor['threshold']

            if value >= threshold and 'above_threshold_direction' in sensor:
                direction = sensor['above_threshold_direction']
            elif 'below_threshold_direction' in sensor:
                direction = sensor['below_threshold_direction']

        return direction


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
                    self._direction = self._get_direction_from_sensors()
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

