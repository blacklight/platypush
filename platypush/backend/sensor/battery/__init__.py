from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorBatteryBackend(SensorBackend):
    """
    This backend listens for battery full/connect/disconnect/below/above threshold events.
    The sensor events triggered by this backend will include any of the following fields:

        - ``battery_percent``
        - ``battery_power_plugged``

    Requires:

        - **psutil** (``pip install psutil``) for CPU load and stats.

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_measurement(self):
        plugin = get_plugin('system')
        battery = plugin.sensors_battery().output

        return {
            'battery_percent': battery.get('percent'),
            'battery_power_plugged': bool(battery.get('power_plugged')),
        }


# vim:sw=4:ts=4:et:
