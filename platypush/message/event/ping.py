from platypush.message.event import Event


class PingEvent(Event):
    """ Ping event, used for testing purposes """

    def __init__(self, message=None, *args, **kwargs):
        """
        :param message: Ping message
        :type message: object
        """

        super().__init__(message=message, *args, **kwargs)


class HostDownEvent(Event):
    """
    Event triggered when a remote host stops responding ping requests.
    """
    def __init__(self, host: str, *args, **kwargs):
        super().__init__(host=host, *args, **kwargs)


class HostUpEvent(Event):
    """
    Event triggered when a remote host starts responding ping requests.
    """
    def __init__(self, host: str, *args, **kwargs):
        super().__init__(host=host, *args, **kwargs)


# vim:sw=4:ts=4:et:
