from platypush.backend.sensor import SensorBackend


class SensorSerialBackend(SensorBackend):
    """
    This backend listens for new events from sensors connected through a serial
    interface (like Arduino) acting as a wrapper for the ``serial`` plugin.

    Requires:

        * The :mod:`platypush.plugins.serial` plugin configured

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def __init__(self, **kwargs):
        super().__init__(plugin='serial', **kwargs)


# vim:sw=4:ts=4:et:
