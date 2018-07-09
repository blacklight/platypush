from platypush.message.event import Event


class IrSensorEvent(Event):
    """
    Base class for infrared sensor events
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IrKeyUpEvent(IrSensorEvent):
    """
    Event triggered when a key on an infrared remote is released
    """

    def __init__(self, message=None, *args, **kwargs):
        """
        :param message: The received infrared message
        """

        super().__init__(*args, message=message, **kwargs)


class IrKeyDownEvent(IrSensorEvent):
    """
    Event triggered when a key on an infrared remote is pressed
    """

    def __init__(self, message=None, *args, **kwargs):
        """
        :param message: The received infrared message
        """

        super().__init__(*args, message=message, **kwargs)


# vim:sw=4:ts=4:et:

