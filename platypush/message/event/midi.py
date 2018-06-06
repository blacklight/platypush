from platypush.message.event import Event


class MidiMessageEvent(Event):
    def __init__(self, message, delay=None, *args, **kwargs):
        super().__init__(*args, message=message, delay=delay, **kwargs)


# vim:sw=4:ts=4:et:

