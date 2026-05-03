from platypush.message.event import Event


class SnapcastEvent(Event):
    """Base class for Snapcast events"""

    def __init__(self, host='localhost', *args, **kwargs):
        super().__init__(*args, host=host, **kwargs)


class ClientConnectedEvent(SnapcastEvent):
    """
    Event fired upon client connection
    """

    def __init__(self, client, host='localhost', *args, **kwargs):
        super().__init__(*args, client=client, host=host, **kwargs)


class ClientDisconnectedEvent(SnapcastEvent):
    """
    Event fired upon client disconnection
    """

    def __init__(self, client, host='localhost', *args, **kwargs):
        super().__init__(*args, client=client, host=host, **kwargs)


class ClientVolumeChangeEvent(SnapcastEvent):
    """
    Event fired upon volume change or mute status change on a client
    """

    def __init__(self, client, volume, muted, host='localhost', *args, **kwargs):
        super().__init__(
            *args, client=client, host=host, volume=volume, muted=muted, **kwargs
        )


class ClientLatencyChangeEvent(SnapcastEvent):
    """
    Event fired upon latency change on a client
    """

    def __init__(self, client, latency, host='localhost', *args, **kwargs):
        super().__init__(*args, client=client, host=host, latency=latency, **kwargs)


class ClientNameChangeEvent(SnapcastEvent):
    """
    Event fired upon name change of a client
    """

    def __init__(self, client, name, host='localhost', *args, **kwargs):
        super().__init__(*args, client=client, host=host, name=name, **kwargs)


class GroupMuteChangeEvent(SnapcastEvent):
    """
    Event fired upon mute status change
    """

    def __init__(self, group, muted, host='localhost', *args, **kwargs):
        super().__init__(*args, group=group, host=host, muted=muted, **kwargs)


class GroupStreamChangeEvent(SnapcastEvent):
    """
    Event fired upon group stream change
    """

    def __init__(self, group, stream, host='localhost', *args, **kwargs):
        super().__init__(*args, group=group, host=host, stream=stream, **kwargs)


class StreamUpdateEvent(SnapcastEvent):
    """
    Event fired upon stream update
    """

    def __init__(self, stream_id, stream, host='localhost', *args, **kwargs):
        super().__init__(*args, stream_id=stream_id, stream=stream, host=host, **kwargs)


class ServerUpdateEvent(SnapcastEvent):
    """
    Event fired upon stream update
    """

    def __init__(self, server, host='localhost', *args, **kwargs):
        super().__init__(*args, server=server, host=host, **kwargs)


# vim:sw=4:ts=4:et:
