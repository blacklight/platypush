from platypush.message.event import Event, EventMatchResult


class PingEvent(Event):
    """ Ping event, used for testing purposes """

    def __init__(self, message=None, *args, **kwargs):
        """
        :param message: Ping message
        :type message: object
        """

        super().__init__(message=message, *args, **kwargs)


# vim:sw=4:ts=4:et:

