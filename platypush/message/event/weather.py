from platypush.message.event import Event

class NewWeatherConditionEvent(Event):
    """
    Event triggered when the weather condition changes
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# vim:sw=4:ts=4:et:

