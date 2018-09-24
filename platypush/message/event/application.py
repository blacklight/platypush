from platypush.message.event import Event


class ApplicationStartedEvent(Event):
    """
    Event triggered when the application has started and all the backends have been registered
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ApplicationStoppedEvent(Event):
    """
    Event triggered when the application stops
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

