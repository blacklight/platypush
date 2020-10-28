from platypush.message.event import Event


class CustomEvent(Event):
    """
    This type can be used to fire custom events upon which the user can implement custom hooks.
    """
    def __init__(self, subtype: str, *args, **kwargs):
        """
        :param subtype: This is the only mandatory attribute for this event type. It should be a string that
            unambiguously identifies a certain type of event (like ``DISHWASHER_STARTED`` or ``SMOKE_DETECTED``).
        :param args: Extra list arguments for the event.
        :param kwargs: Extra key-value arguments for the event.
        """
        super().__init__(*args, subtype=subtype, **kwargs)


# vim:sw=4:ts=4:et:
