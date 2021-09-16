from platypush.backend.sensor import SensorBackend


class SensorMcp3008Backend(SensorBackend):
    """
    Backend to poll analog sensor values from an MCP3008 chipset
    (https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008)

    Requires:

        * ``adafruit-mcp3008`` (``pip install adafruit-mcp3008``)
        * The :mod:`platypush.plugins.gpio.sensor.mcp3008` plugin configured

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def __init__(self, **kwargs):
        super().__init__(plugin='gpio.sensor.mcp3008', **kwargs)


# vim:sw=4:ts=4:et:
