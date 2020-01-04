from platypush.backend.sensor import SensorBackend


class SensorArduinoBackend(SensorBackend):
    """
    This backend listens for new events from an Arduino with a Firmata-compatible firmware.

    Requires:

        * The :class:`platypush.plugins.arduino.ArduinoPlugin` plugin configured.

    """

    def __init__(self, **kwargs):
        super().__init__(plugin='arduino', **kwargs)


# vim:sw=4:ts=4:et:
