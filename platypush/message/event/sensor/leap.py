from platypush.message.event import Event


class LeapFrameEvent(Event):
    """
    Event triggered when a Leap Motion devices receives a new frame
    """

    def __init__(self, hands, *args, **kwargs):
        """
        :param hands: Reference to the detected hands properties (palm and fingers X,Y,Z position, direction etc.)
        :type hands: dict
        """

        super().__init__(hands=hands, *args, **kwargs)


class LeapFrameStartEvent(Event):
    """
    Event triggered when a new sequence of frames is detected by the Leap Motion sensor
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LeapFrameStopEvent(Event):
    """
    Event triggered when a Leap Sensor stops detecting frames
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LeapConnectEvent(Event):
    """
    Event triggered when a Leap Motion sensor is connected
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LeapDisconnectEvent(Event):
    """
    Event triggered when a Leap Motion sensor is disconnected
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

