import logging
import json
import time

from kafka import KafkaConsumer, KafkaProducer

from .. import Backend

class KafkaBackend(Backend):
    _conn_retry_secs = 5

    def __init__(self, server, topic, **kwargs):
        super().__init__(**kwargs)

        self.server = server
        self.topic_prefix = topic
        self.topic = self._topic_by_device_id(self.device_id)
        self.producer = None

        logging.getLogger('kafka').setLevel(logging.ERROR)

    def _on_record(self, record):
        if record.topic != self.topic: return

        try:
            msg = json.loads(record.value.decode('utf-8'))
        except Exception as e:
            logging.exception(e)

        logging.debug('Received message on Kafka backend: {}'.format(msg))
        self.on_message(msg)

    def _init_producer(self):
        if not self.producer:
            self.producer = KafkaProducer(bootstrap_servers=self.server)

    def _topic_by_device_id(self, device_id):
        return '{}.{}'.format(self.topic_prefix, device_id)

    def send_message(self, msg):
        target = msg.target
        msg = str(msg).encode('utf-8')

        self._init_producer()
        self.producer.send(self._topic_by_device_id(target), msg)
        self.producer.flush()

    def on_stop(self):
        try:
            if self.producer:
                self.producer.flush()
                self.producer.close()

            if self.consumer:
                self.consumer.close()
        except Exception as e:
            logging.warning('Exception occurred while closing Kafka connection')
            logging.exception(e)

    def run(self):
        super().run()

        self.consumer = KafkaConsumer(self.topic, bootstrap_servers=self.server)
        logging.info('Initialized kafka backend - server: {}, topic: {}'
                     .format(self.server, self.topic))

        try:
            for msg in self.consumer:
                self._on_record(msg)
                if self.should_stop(): break
        except Exception as e:
            logging.warning('Kafka connection error, reconnecting in {} seconds'.
                            format(self._conn_retry_secs))
            logging.exception(e)
            time.sleep(self._conn_retry_secs)

# vim:sw=4:ts=4:et:

