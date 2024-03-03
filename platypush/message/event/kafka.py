from typing import Union
from platypush.message.event import Event


class KafkaMessageEvent(Event):
    """
    Kafka message event object. Fired when :mod:`platypush.backend.kafka` receives
    a new event.
    """

    def __init__(
        self,
        *args,
        msg: Union[str, list, dict],
        topic: str,
        host: str,
        port: int,
        **kwargs
    ):
        """
        :param msg: Received message. If the message is a JSON string, it will
            be returned as a dict or list. If it's a binary blob, it will be
            returned as a base64-encoded string.
        :param topic: Topic where the message was received.
        :param host: Host where the message was received.
        :param port: Port where the message was received.
        """
        super().__init__(*args, msg=msg, topic=topic, host=host, port=port, **kwargs)


# vim:sw=4:ts=4:et:
