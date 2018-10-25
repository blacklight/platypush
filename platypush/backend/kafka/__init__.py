import json
import logging
import time

from kafka import KafkaConsumer, KafkaProducer

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message import Message
from platypush.message.event.kafka import KafkaMessageEvent


class KafkaBackend(Backend):
    """
    Backend to interact with an Apache Kafka (https://kafka.apache.org/)
    streaming platform, send and receive messages.

    Requires:

        * **kafka** (``pip install kafka-python``)
    """

    _conn_retry_secs = 5

    def __init__(self, server='localhost:9092', topic='platypush', **kwargs):
        """
        :param server: Kafka server name or address + port (default: ``localhost:9092``)
        :type server: str

        :param topic: (Prefix) topic to listen to (default: platypush). The Platypush device_id (by default the hostname) will be appended to the topic (the real topic name will e.g. be "platypush.my_rpi")
        :type topic: str
        """

        super().__init__(**kwargs)

        self.server = server
        self.topic_prefix = topic
        self.topic = self._topic_by_device_id(self.device_id)
        self.producer = None

        # Kafka can be veryyyy noisy
        logging.getLogger('kafka').setLevel(logging.ERROR)

    def _on_record(self, record):
        if record.topic != self.topic: return
        msg = record.value.decode('utf-8')
        is_platypush_message = False

        try:
            msg = Message.build(msg)
            is_platypush_message = True
        except:
            pass

        self.logger.info('Received message on Kafka backend: {}'.format(msg))

        if is_platypush_message:
            self.on_message(msg)
        else:
            self.on_message(KafkaMessageEvent(msg=msg))

    def _topic_by_device_id(self, device_id):
        return '{}.{}'.format(self.topic_prefix, device_id)

    def send_message(self, msg):
        target = msg.target
        kafka_plugin = get_plugin('kafka')
        kafka_plugin.send_message(msg=msg,
                                  topic=self._topic_by_device_id(target),
                                  server=self.server)

    def on_stop(self):
        try:
            if self.producer:
                self.producer.flush()
                self.producer.close()

            if self.consumer:
                self.consumer.close()
        except Exception as e:
            self.logger.warning('Exception occurred while closing Kafka connection')
            self.logger.exception(e)

    def run(self):
        super().run()

        self.consumer = KafkaConsumer(self.topic, bootstrap_servers=self.server)
        self.logger.info('Initialized kafka backend - server: {}, topic: {}'
                     .format(self.server, self.topic))

        try:
            for msg in self.consumer:
                self._on_record(msg)
                if self.should_stop(): break
        except Exception as e:
            self.logger.warning('Kafka connection error, reconnecting in {} seconds'.
                            format(self._conn_retry_secs))
            self.logger.exception(e)
            time.sleep(self._conn_retry_secs)

# vim:sw=4:ts=4:et:

