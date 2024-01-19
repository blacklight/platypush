from platypush.message.event import Event


class AdafruitConnectedEvent(Event):
    """
    Event triggered when the backend connects to the Adafruit message queue.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AdafruitDisconnectedEvent(Event):
    """
    Event triggered when the backend disconnects from the Adafruit message
    queue.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AdafruitFeedUpdateEvent(Event):
    """
    Event triggered when a message is received on a subscribed Adafruit feed.
    """

    def __init__(self, feed, data, *args, **kwargs):
        super().__init__(*args, feed=feed, data=data, **kwargs)


# vim:sw=4:ts=4:et:
