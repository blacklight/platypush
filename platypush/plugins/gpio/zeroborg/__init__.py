import enum
import threading
import time

from platypush.plugins import Plugin, action
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
    """
    ZeroBorg plugin. It allows you to control a ZeroBorg
    (https://www.piborg.org/motor-control-1135/zeroborg) motor controller and
    infrared sensor circuitry for Raspberry Pi
    """

    _drive_thread = None
    _can_run = False
    _direction = None


    def __init__(self, directions = {}, *args, **kwargs):
        """
        :param directions: Configuration for the motor directions. A direction is basically a configuration of the power delivered to each motor to allow whichever object you're controlling (wheels, robotic arms etc.) to move in a certain direction. In my experience the ZeroBorg always needs a bit of calibration, depending on factory defaults and the mechanical properties of the load it controls.

        Example configuration that I use to control a simple 4WD robot::

            directions = {
                "up": {
                    "motor_1_power": 0.4821428571428572,
                    "motor_2_power": 0.4821428571428572,
                    "motor_3_power": -0.6707142857142858,
                    "motor_4_power": -0.6707142857142858
                },
                "down": {
                    "motor_1_power": -0.4821428571428572,
                    "motor_2_power": -0.4821428571428572,
                    "motor_3_power": 0.825,
                    "motor_4_power": 0.825
                },
                "left": {
                    "motor_1_power": -0.1392857142857143,
                    "motor_2_power": -0.1392857142857143,
                    "motor_3_power": -1.0553571428571429,
                    "motor_4_power": -1.0553571428571429
                },
                "right": {
                    "motor_1_power": 1.0017857142857143,
                    "motor_2_power": 1.0017857142857143,
                    "motor_3_power": 0.6214285714285713,
                    "motor_4_power": 0.6214285714285713
                },
                "auto": {
                    "sensors": [
                        {
                            "plugin": "gpio.sensor.distance",
                            "threshold": 400.0,
                            "timeout": 2.0,
                            "above_threshold_direction": "up",
                            "below_threshold_direction": "left"
                        }
                    ]
                }
            }

        Note that the special direction "auto" can contain a configuration that allows your device to move autonomously based on the inputs it gets from some sensors.  In this case, I set the sensors configuration (a list) to periodically poll a GPIO-based ultrasound distance sensor plugin. ``timeout`` says after how long a poll attempt should fail. The plugin package is specified through ``plugin`` (``gpio.sensor.distance``) in this case, note that the plugin must be configured as well in order to work). The ``threshold`` value says around which value your logic should trigger. In this case, threshold=400 (40 cm). When the distance value is above that threshold (``above_threshold_direction``), then go "up" (no obstacles ahead). Otherwise (``below_threshold_direction``), turn "left" (avoid the obstacle).

        :type directions: dict
        """

        import platypush.plugins.gpio.zeroborg.lib as ZeroBorg
        super().__init__(*args, **kwargs)

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
            value = plugin.get_measurement().output
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

            self.logger.info('Sensor: {}\tMeasurement: {}\tDirection: {}'
                         .format(sensor['plugin'], value, direction))

        return direction


    @action
    def drive(self, direction):
        """
        Drive the motors in a certain direction.

        :param direction: Direction name (note: it must be a configured direction). Special directions:
            * ``auto`` - Enter automatic drive mode
            * ``auto_toggle`` - Toggle automatic drive mode (on or off)
            * ``stop`` - Turn off the motors

        """

        prev_direction = self._direction

        self._can_run = True
        self._direction = direction.lower()
        self.logger.info('Received ZeroBorg drive command: {}'.format(direction))

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
                    self.logger.warning('Invalid direction {}, stopping motors'.format(self._direction))

                self.zb.SetMotor1(motor_1_power)
                self.zb.SetMotor2(motor_2_power)
                self.zb.SetMotor3(motor_3_power)
                self.zb.SetMotor4(motor_4_power)

            self.auto_mode = False


        self._drive_thread = threading.Thread(target=_run)
        self._drive_thread.start()

        return {'status': 'running', 'direction': direction}


    @action
    def stop(self):
        """
        Turns off the motors
        """

        self._can_run = False
        if self._drive_thread and threading.get_ident() != self._drive_thread.ident:
            self._drive_thread.join()

        self.zb.MotorsOff()
        self.zb.ResetEpo()

        return {'status':'stopped'}


# vim:sw=4:ts=4:et:

