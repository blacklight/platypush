from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorSerialBackend(SensorBackend):
    """
    This backend listens for new events from sensors connected through a serial
    interface (like Arduino) acting as a wrapper for the ``serial`` plugin.

    Requires:

        * The :mod:`platypush.plugins.serial` plugin configured
    """

    def get_measurement(self):
        """ Implemnetation of ``get_measurement`` """
        plugin = get_plugin('serial')
        return plugin.get_data().output


# vim:sw=4:ts=4:et:

