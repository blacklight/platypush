from platypush.message.event import Event


class LightOnEvent(Event):
    """
    Event triggered when a light on event is detected
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LightOffEvent(Event):
    """
    Event triggered when a light off event is detected
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

