from platypush.backend.sensor import SensorBackend


class SensorMotionPmw3901Backend(SensorBackend):
    """
    Backend to poll an `PMW3901 <https://github.com/pimoroni/pmw3901-python>`_
    optical flow and motion sensor

    Requires:

        * ``pmw3901`` (``pip install pmw3901``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    _default_poll_seconds = 0.01

    def __init__(self, **kwargs):
        if 'poll_seconds' not in kwargs:
            # noinspection PyTypeChecker
            kwargs['poll_seconds'] = self._default_poll_seconds

        super().__init__(plugin='gpio.sensor.motion.pmw3901', **kwargs)


# vim:sw=4:ts=4:et:
