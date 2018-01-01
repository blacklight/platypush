from platypush.message.event import Event, EventMatchResult


class PingEvent(Event):
    """ Ping event """

    def __init__(self, message=None, *args, **kwargs):
        super().__init__(message=message, *args, **kwargs)


# vim:sw=4:ts=4:et:

