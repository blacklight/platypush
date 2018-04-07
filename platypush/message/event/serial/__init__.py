from platypush.message.event import Event


class SerialDataEvent(Event):
    def __init__(self, data, device=None, *args, **kwargs):
        super().__init__(data=data, device=device, *args, **kwargs)


# vim:sw=4:ts=4:et:

