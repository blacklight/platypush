from platypush.message.event import Event


class GooglePubsubMessageEvent(Event):
    """
    Event triggered when a new message is received on a subscribed Google Pub/Sub topic.
    """

    def __init__(self, topic: str, msg, *args, **kwargs):
        super().__init__(*args, topic=topic, msg=msg, *args, **kwargs)


# vim:sw=4:ts=4:et:
