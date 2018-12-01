from platypush.message.event import Event


class WiimoteEvent(Event):
    """
    Event triggered upon Wiimote event
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WiimoteConnectionEvent(WiimoteEvent):
    """
    Event triggered upon Wiimote connection
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WiimoteDisconnectionEvent(WiimoteEvent):
    """
    Event triggered upon Wiimote disconnection
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

