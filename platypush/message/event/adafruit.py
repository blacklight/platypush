from platypush.message.event import Event


class ConnectedEvent(Event):
    """
    Event triggered when the backend connects to the Adafruit message queue
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, feed=feed, data=data, **kwargs)


class DisconnectedEvent(Event):
    """
    Event triggered when the backend disconnects from the Adafruit message queue
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, feed=feed, data=data, **kwargs)


class FeedUpdateEvent(Event):
    """
    Event triggered upon Adafruit IO feed update
    """

    def __init__(self, feed, data, *args, **kwargs):
        super().__init__(*args, feed=feed, data=data, **kwargs)


# vim:sw=4:ts=4:et:
