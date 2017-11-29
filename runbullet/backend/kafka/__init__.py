import logging
import json

from kafka import KafkaConsumer, KafkaProducer

from .. import Backend

class KafkaBackend(Backend):
    def _init(self, server, topic):
        self.server = server
        self.topic = topic

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
        if isinstance(msg, bytes):
            msg = msg.encode('utf-8')
        if isinstance(msg, str):
            msg = json.dumps(msg)
        if not isinstance(msg, dict):
            raise RuntimeError('Invalid non-JSON message')

        self._init_producer()
        self.producer.send(self.topic, msg)

    def run(self):
        self.producer = None
        self.consumer = KafkaConsumer(self.topic, bootstrap_servers=self.server)
        for msg in self.consumer:
            self._on_record(msg)

# vim:sw=4:ts=4:et:

