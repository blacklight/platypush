from platypush.backend.sensor import SensorBackend


class SensorSerialBackend(SensorBackend):
    """
    This backend listens for new events from sensors connected through a serial
    interface (like Arduino) acting as a wrapper for the ``serial`` plugin.

    Requires:

        * The :mod:`platypush.plugins.serial` plugin configured
    """

    def __init__(self, **kwargs):
        super().__init__(plugin='serial', **kwargs)


# vim:sw=4:ts=4:et:
