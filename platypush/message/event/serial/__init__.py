from platypush.message.event import Event


class SerialDataEvent(Event):
    """
    Event fired when a serial interface (generic USB, Arduino etc.) receives new data
    """

    def __init__(self, data, device=None, *args, **kwargs):
        """
        :param data: Received data
        :type data: object

        :param device: Source device address or name
        :type device: str
        """

        super().__init__(data=data, device=device, *args, **kwargs)


# vim:sw=4:ts=4:et:

