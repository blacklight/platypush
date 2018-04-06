from platypush.message.event import Event


class LightOnEvent(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LightOffEvent(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

