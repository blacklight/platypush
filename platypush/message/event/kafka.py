from platypush.message.event import Event


class KafkaMessageEvent(Event):
    """
    Kafka message event object. Fired when :mod:`platypush.backend.kafka` receives
    a new event.
    """

    def __init__(self, msg, *args, **kwargs):
        """
        :param msg: Received message
        :type msg: str or bytes stream
        """

        super().__init__(msg=msg, *args, **kwargs)


# vim:sw=4:ts=4:et:

