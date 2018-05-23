from platypush.message.event import Event


class LeapFrameEvent(Event):
    def __init__(self, hands, *args, **kwargs):
        super().__init__(hands=hands, *args, **kwargs)


class LeapFrameStartEvent(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LeapFrameStopEvent(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LeapConnectEvent(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LeapDisconnectEvent(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

