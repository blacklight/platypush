from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin


class SensorBatteryBackend(SensorBackend):
    """
    This backend listens for battery full/connect/disconnect/below/above threshold events.
    The sensor events triggered by this backend will include any of the following fields:

        - ``battery_percent``
        - ``battery_secs_left``
        - ``battery_power_plugged``

    Requires:

        - **psutil** (``pip install psutil``) for CPU load and stats.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_measurement(self):
        plugin = get_plugin('system')
        return {
            'battery_' + name: value
            for name, value in plugin.sensors_battery().output.items()
        }


# vim:sw=4:ts=4:et:
