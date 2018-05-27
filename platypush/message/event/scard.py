from platypush.message.event import Event


class SmartCardDetectedEvent(Event):
    def __init__(self, atr, reader=None, *args, **kwargs):
        super().__init__(atr=atr, reader=reader, *args, **kwargs)


# vim:sw=4:ts=4:et:

