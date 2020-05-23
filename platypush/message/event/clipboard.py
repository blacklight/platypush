from platypush.message.event import Event


class ClipboardEvent(Event):
    def __init__(self, text: str, *args, **kwargs):
        super().__init__(*args, text=text, **kwargs)


# vim:sw=4:ts=4:et:
