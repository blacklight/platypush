from typing import Optional

from platypush.message.event import Event


class NewWeatherConditionEvent(Event):
    """
    Event triggered when the weather condition changes
    """

    def __init__(self, *args, plugin_name: Optional[str] = None, **kwargs):
        super().__init__(*args, plugin_name=plugin_name, **kwargs)


class NewPrecipitationForecastEvent(Event):
    """
    Event triggered when the precipitation forecast changes
    """
    def __init__(self, *args, plugin_name: Optional[str] = None, average: float, total: float,
                 time_frame: int, **kwargs):
        super().__init__(*args, plugin_name=plugin_name, average=average, total=total, time_frame=time_frame, **kwargs)


# vim:sw=4:ts=4:et:
