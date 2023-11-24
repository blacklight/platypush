from platypush.message.event import Event


class PingEvent(Event):
    """Ping event, used for testing purposes"""

    def __init__(self, *args, message=None, **kwargs):
        """
        :param message: Ping message
        :type message: object
        """

        super().__init__(*args, message=message, **kwargs)


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


class PingResponseEvent(Event):
    """
    Event triggered when a ping response is received.
    """

    def __init__(
        self,
        host: str,
        min: float,
        max: float,
        avg: float,
        mdev: float,
        *args,
        **kwargs
    ):
        """
        :param host: Remote host IP or name.
        :param min: Minimum round-trip time (in ms).
        :param max: Maximum round-trip time (in ms).
        :param avg: Average round-trip time (in ms).
        :param mdev: Standard deviation of the round-trip time (in ms).
        """
        super().__init__(
            host=host, min=min, max=max, avg=avg, mdev=mdev, *args, **kwargs
        )


# vim:sw=4:ts=4:et:
