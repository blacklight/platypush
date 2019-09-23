from platypush.backend.sensor import SensorBackend


class SensorMotionPwm3901Backend(SensorBackend):
    """
    Backend to poll an `PWM3901 <https://github.com/pimoroni/pmw3901-python>`_
    optical flow and motion sensor

    Requires:

        * ``pwm3901`` (``pip install pwm3901``)
    """

    _default_poll_seconds = 0.01

    def __init__(self, absolute=True, relative=True, **kwargs):
        """
        :param absolute: Enable absolute motion sensor events (default: true)
        :param relative: Enable relative motion sensor events (default: true)
        """

        enabled_sensors = {
            'motion_rel_x': relative,
            'motion_rel_y': relative,
            'motion_rel_mod': relative,
            'motion_abs_x': absolute,
            'motion_abs_y': absolute,
            'motion_abs_mod': absolute,
        }

        if 'poll_seconds' not in kwargs:
            # noinspection PyTypeChecker
            kwargs['poll_seconds'] = self._default_poll_seconds

        super().__init__(plugin='gpio.sensor.motion.pwm3901', enabled_sensors=enabled_sensors, **kwargs)


# vim:sw=4:ts=4:et:
