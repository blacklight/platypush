from platypush.message.event import Event


class MidiMessageEvent(Event):
    """
    Event triggered upon received MIDI message
    """

    def __init__(self, message, delay=None, *args, **kwargs):
        """
        :param message: Received MIDI message
        :type message: tuple[int]

        :param delay: Time in seconds since the previous MIDI event (default: None)
        :type delay: float
        """

        super().__init__(*args, message=message, delay=delay, **kwargs)


# vim:sw=4:ts=4:et:

