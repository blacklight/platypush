import logging
import json

from kafka import KafkaConsumer, KafkaProducer

from .. import Backend

class KafkaBackend(Backend):
    def _init(self, server, topic):
        self.server = server
        self.topic = topic
        self.producer = None

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

    def send_msg(self, msg):
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        if not isinstance(msg, bytes):
            msg = json.dumps(msg)
            raise RuntimeError('Invalid non-JSON message')

        self._init_producer()
        self.producer.send(self.topic, msg)
        self.producer.flush()

    def run(self):
        self.consumer = KafkaConsumer(self.topic, bootstrap_servers=self.server)
        logging.info('Initialized kafka backend - server: {}, topic: {}'
                     .format(self.server, self.topic))

        for msg in self.consumer:
            self._on_record(msg)

# vim:sw=4:ts=4:et:

