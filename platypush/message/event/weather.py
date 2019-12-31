from platypush.message.event import Event


class NewWeatherConditionEvent(Event):
    """
    Event triggered when the weather condition changes
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NewPrecipitationForecastEvent(Event):
    """
    Event triggered when the precipitation forecast changes
    """
    def __init__(self, *args, average: float, total: float, time_frame: int, **kwargs):
        super().__init__(*args, average=average, total=total, time_frame=time_frame, **kwargs)


# vim:sw=4:ts=4:et:
