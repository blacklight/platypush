from platypush.message.event import Event


class WidgetUpdateEvent(Event):
    def __init__(self, widget, *args, **kwargs):
        super().__init__(widget=widget, *args, **kwargs)


# vim:sw=4:ts=4:et:

