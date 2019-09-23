from platypush.backend.sensor import SensorBackend


class SensorMotionPwm3901Backend(SensorBackend):
    """
    Backend to poll an `PWM3901 <https://github.com/pimoroni/pmw3901-python>`_
    optical flow and motion sensor

    Requires:

        * ``pwm3901`` (``pip install pwm3901``)
    """

    _default_poll_seconds = 0.01

    def __init__(self, **kwargs):
        if 'poll_seconds' not in kwargs:
            # noinspection PyTypeChecker
            kwargs['poll_seconds'] = self._default_poll_seconds

        super().__init__(plugin='gpio.sensor.motion.pwm3901', **kwargs)


# vim:sw=4:ts=4:et:
