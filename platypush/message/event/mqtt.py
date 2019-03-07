from platypush.message.event import Event


class MQTTMessageEvent(Event):
    """
    MQTT message event object. Fired when :mod:`platypush.backend.mqtt` receives
    a new event.
    """

    def __init__(self, msg, host=None, port=None, topic=None, *args, **kwargs):
        super().__init__(msg=msg, host=host, port=port, topic=topic,
                         *args, **kwargs)


# vim:sw=4:ts=4:et:
