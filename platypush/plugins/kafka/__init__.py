import json
import logging

from platypush.context import get_backend
from platypush.plugins import Plugin, action


class KafkaPlugin(Plugin):
    """
    Plugin to send messages to an Apache Kafka instance (https://kafka.apache.org/)

    Triggers:

        * :class:`platypush.message.event.kafka.KafkaMessageEvent` when a new message is received on the consumer topic.

    Requires:

        * **kafka** (``pip install kafka-python``)
    """

    def __init__(self, server=None, port=9092, **kwargs):
        """
        :param server: Default Kafka server name or address. If None (default), then it has to be specified upon
            message sending.
        :type server: str

        :param port: Default Kafka server port (default: 9092).
        :type port: int
        """

        super().__init__(**kwargs)

        self.server = '{server}:{port}'.format(server=server, port=port) \
            if server else None

        self.producer = None

        # Kafka can be veryyyy noisy
        logging.getLogger('kafka').setLevel(logging.ERROR)

    @action
    def send_message(self, msg, topic, server=None):
        """
        :param msg: Message to send - as a string, bytes stream, JSON, Platypush message, dictionary, or anything
            that implements ``__str__``

        :param topic: Topic to send the message to.
        :type topic: str

        :param server: Kafka server name or address + port (format: ``host:port``). If None, then the default server
            will be used
        :type server: str
        """

        from kafka import KafkaProducer

        if not server:
            if not self.server:
                try:
                    kafka_backend = get_backend('kafka')
                    server = kafka_backend.server
                except Exception as e:
                    raise RuntimeError(f'No Kafka server nor default server specified: {str(e)}')
            else:
                server = self.server

        if isinstance(msg, dict) or isinstance(msg, list):
            msg = json.dumps(msg)
        msg = str(msg).encode('utf-8')

        producer = KafkaProducer(bootstrap_servers=server)
        producer.send(topic, msg)
        producer.flush()


# vim:sw=4:ts=4:et:
