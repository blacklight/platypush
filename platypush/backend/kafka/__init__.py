import logging
import json

from kafka import KafkaConsumer, KafkaProducer

from .. import Backend

class KafkaBackend(Backend):
    def __init__(self, server, topic, **kwargs):
        super().__init__(**kwargs)

        self.server = server
        self.topic_prefix = topic
        self.topic = self._topic_by_device_id(self.device_id)
        self.producer = None
        self._init_producer()

    def _on_record(self, record):
        if record.topic != self.topic: return

        try:
            msg = json.loads(record.value.decode('utf-8'))
        except Exception as e:
            logging.exception(e)

        logging.debug('Received message: {}'.format(msg))
        self.on_msg(msg)

    def _init_producer(self):
        if not self.producer:
            self.producer = KafkaProducer(bootstrap_servers=self.server)

    def _topic_by_device_id(self, device_id):
        return '{}.{}'.format(self.topic_prefix, device_id)

    def _send_msg(self, msg):
        target = msg.target
        msg = str(msg).encode('utf-8')

        self._init_producer()
        self.producer.send(self._topic_by_device_id(target), msg)
        self.producer.flush()

    def run(self):
        self.consumer = KafkaConsumer(self.topic, bootstrap_servers=self.server)
        logging.info('Initialized kafka backend - server: {}, topic: {}'
                     .format(self.server, self.topic))

        for msg in self.consumer:
            self._on_record(msg)

# vim:sw=4:ts=4:et:

