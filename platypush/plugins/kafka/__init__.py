import base64
import json
import logging
from collections import defaultdict
from threading import RLock, Thread
from typing import Dict, Iterable, Optional, Union

from kafka import KafkaConsumer, KafkaProducer

from platypush.message.event.kafka import KafkaMessageEvent
from platypush.plugins import RunnablePlugin, action


class KafkaPlugin(RunnablePlugin):
    """
    Plugin to send messages to an Apache Kafka instance (https://kafka.apache.org/)
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 9092,
        listeners: Optional[Iterable[dict]] = None,
        connection_retry_secs: float = 5.0,
        **kwargs,
    ):
        """
        :param host: Default Kafka server name or address. If None (default),
            then it has to be specified when calling the ``send_message`` action.
        :param port: Default Kafka server port (default: 9092).
        :param connection_retry_secs: Seconds to wait before retrying to
            connect to the Kafka server after a connection error (default: 5).
        :param listeners: If specified, the Kafka plugin will listen for
            messages on these topics. Use this parameter if you also want to
            listen on other Kafka brokers other than the primary one. This
            parameter supports a list of maps, where each item supports the
            same arguments passed to the main configuration (host, port, topic,
            password etc.). If host/port are omitted, then the host/port value
            from the plugin configuration will be used. If any of the other
            fields are omitted, then their default value will be used (usually
            null). Example:

                .. code-block:: yaml

                    listeners:
                        # This listener use the default configured host/port
                        - topics:
                              - topic1
                              - topic2
                              - topic3

                        # This will use a custom MQTT broker host
                        - host: sensors
                          port: 19200
                          username: myuser
                          password: secret
                          topics:
                              - topic4
                              - topic5

        """

        super().__init__(**kwargs)

        self.host = host
        self.port = port
        self._conn_retry_secs = connection_retry_secs
        self._listeners = listeners or []

        # `server:port` -> KafkaProducer mapping
        self.producers: Dict[str, KafkaProducer] = {}
        # `server:port` -> KafkaConsumer mapping
        self.consumers: Dict[str, KafkaConsumer] = {}

        # Synchronization locks for the producers/consumers maps,
        # since python-kafka is not thread-safe
        self._producers_locks = defaultdict(RLock)
        self._consumers_locks = defaultdict(RLock)

        # Kafka can be very noisy
        logging.getLogger('kafka').setLevel(logging.ERROR)

    def _get_srv_str(
        self, host: Optional[str] = None, port: Optional[int] = None
    ) -> str:
        if not host:
            host = self.host

        assert host, 'No Kafka server specified'
        if not port:
            port = self.port

        return f'{host}:{port}'

    def _get_producer(
        self, host: Optional[str] = None, port: Optional[int] = None, **kwargs
    ):
        srv_str = self._get_srv_str(host, port)
        with self._producers_locks[srv_str]:
            if srv_str not in self.producers:
                self.producers[srv_str] = KafkaProducer(
                    bootstrap_servers=srv_str, **kwargs
                )
            return self.producers[srv_str]

    def _get_consumer(
        self, host: Optional[str] = None, port: Optional[int] = None, **kwargs
    ):
        srv_str = self._get_srv_str(host, port)
        with self._consumers_locks[srv_str]:
            if srv_str not in self.consumers:
                self.consumers[srv_str] = KafkaConsumer(
                    bootstrap_servers=srv_str, **kwargs
                )
            return self.consumers[srv_str]

    def _on_msg(self, record, host: str, port: int):
        try:
            msg = record.value.decode()
        except UnicodeDecodeError:
            msg = base64.b64encode(record.value).decode()

        try:
            msg = json.loads(msg)
        except (TypeError, ValueError):
            pass

        self._bus.post(
            KafkaMessageEvent(msg=msg, topic=record.topic, host=host, port=port)
        )

    def _consumer_monitor(self, consumer: KafkaConsumer, host: str, port: int):
        while not self.should_stop():
            try:
                for msg in consumer:
                    self._on_msg(msg, host=host, port=port)
                    if self.should_stop():
                        break
            except Exception as e:
                if not self.should_stop():
                    self.logger.exception(e)
                    self.logger.warning(
                        'Kafka connection error to %s:%d, reconnecting in %f seconds',
                        host,
                        port,
                        self._conn_retry_secs,
                    )

                self.wait_stop(self._conn_retry_secs)

    @action
    def publish(self, msg: Union[str, list, dict, tuple, bytes], topic: str, **kwargs):
        """
        :param msg: Message to send.
        :param topic: Topic to send the message to.
        :param kwargs: Additional arguments to pass to the KafkaConsumer,
            including ``host`` and ``port``.
        """
        if isinstance(msg, tuple):
            msg = list(msg)
        if isinstance(msg, (dict, list)):
            msg = json.dumps(msg)
        if not isinstance(msg, bytes):
            msg = str(msg).encode()

        producer = self._get_producer(**kwargs)
        producer.send(topic, msg)
        producer.flush()

    @action
    def send_message(
        self, msg: Union[str, list, dict, tuple, bytes], topic: str, **kwargs
    ):
        """
        Alias for :meth:`.publish`.
        """
        return self.send_message(msg=msg, topic=topic, **kwargs)

    @action
    def subscribe(self, topic: str, **kwargs):
        """
        Subscribe to a topic.

        :param topic: Topic to subscribe to.
        :param kwargs: Additional arguments to pass to the KafkaConsumer,
            including ``host`` and ``port``.
        """
        consumer = self._get_consumer(**kwargs)
        consumer.subscribe([topic])

    @action
    def unsubscribe(self, **kwargs):
        """
        Unsubscribe from all the topics on a consumer.

        :param kwargs: Additional arguments to pass to the KafkaConsumer,
            including ``host`` and ``port``.
        """
        consumer = self._get_consumer(**kwargs)
        consumer.unsubscribe()

    def main(self):
        for listener in self._listeners:
            host = listener.get('host', self.host)
            port = listener.get('port', self.port)
            topics = listener.get('topics')
            if not topics:
                continue

            consumer = self._get_consumer(
                host=host,
                port=port,
                group_id='platypush',
                auto_offset_reset='earliest',
            )

            consumer.subscribe(topics)
            Thread(
                target=self._consumer_monitor,
                args=(consumer,),
                kwargs={'host': host, 'port': port},
                daemon=True,
            ).start()

        self.wait_stop()

    def stop(self):
        super().stop()
        for srv, producer in self.producers.items():
            try:
                producer.flush()
                producer.close()
            except Exception as e:
                self.logger.warning('Error while closing Kafka producer %s: %s', srv, e)

        for srv, consumer in self.consumers.items():
            try:
                consumer.close()
            except Exception as e:
                self.logger.warning('Error while closing Kafka consumer %s: %s', srv, e)


# vim:sw=4:ts=4:et:
