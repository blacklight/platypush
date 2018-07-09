from platypush.message.event import Event


class SmartCardDetectedEvent(Event):
    """
    Event triggered when a smart card is detected
    """

    def __init__(self, atr, reader=None, *args, **kwargs):
        """
        :param atr: Smart card ATR (Answer To Reset)
        :type atr: str

        :param reader: Name or address of the reader that fired the event
        :type reader: str
        """

        super().__init__(atr=atr, reader=reader, *args, **kwargs)


class SmartCardRemovedEvent(Event):
    """
    Event triggered when a smart card is removed
    """

    def __init__(self, atr=None, reader=None, *args, **kwargs):
        """
        :param atr: Smart card ATR (Answer To Reset)
        :type atr: str

        :param reader: Name or address of the reader that fired the event
        :type reader: str
        """

        super().__init__(atr=atr, reader=reader, *args, **kwargs)


# vim:sw=4:ts=4:et:

