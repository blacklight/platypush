from platypush.message.event import Event


class WidgetUpdateEvent(Event):
    """
    Event delivered to the dashboard when a widget update request is delivered to it
    """

    def __init__(self, widget, *args, **kwargs):
        """
        :param widget: Widget ID
        :type widget: str
        """

        super().__init__(widget=widget, *args, **kwargs)


# vim:sw=4:ts=4:et:

