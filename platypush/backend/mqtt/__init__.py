import hashlib
import json
import os
import threading
from typing import Any, Dict, Optional, List, Callable

import paho.mqtt.client as mqtt

from platypush.backend import Backend
from platypush.config import Config
from platypush.context import get_plugin
from platypush.message import Message
from platypush.message.event.mqtt import MQTTMessageEvent
from platypush.message.request import Request
from platypush.plugins.mqtt import MqttPlugin as MQTTPlugin


class MqttClient(mqtt.Client, threading.Thread):
    """
    Wrapper class for an MQTT client executed in a separate thread.
    """

    def __init__(
        self,
        *args,
        host: str,
        port: int,
        topics: Optional[List[str]] = None,
        on_message: Optional[Callable] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        tls_cafile: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version=None,
        tls_ciphers=None,
        tls_insecure: bool = False,
        keepalive: Optional[int] = 60,
        **kwargs,
    ):
        mqtt.Client.__init__(self, *args, client_id=client_id, **kwargs)
        threading.Thread.__init__(self)

        self.name = f'MQTTClient:{client_id}'
        self.host = host
        self.port = port
        self.topics = set(topics or [])
        self.keepalive = keepalive
        self.on_connect = self.connect_hndl()

        if on_message:
            self.on_message = on_message

        if username and password:
            self.username_pw_set(username, password)

        if tls_cafile:
            self.tls_set(
                ca_certs=tls_cafile,
                certfile=tls_certfile,
                keyfile=tls_keyfile,
                tls_version=tls_version,
                ciphers=tls_ciphers,
            )

            self.tls_insecure_set(tls_insecure)

        self._running = False
        self._stop_scheduled = False

    def subscribe(self, *topics, **kwargs):
        """
        Client subscription handler.
        """
        if not topics:
            topics = self.topics

        self.topics.update(topics)
        for topic in topics:
            super().subscribe(topic, **kwargs)

    def unsubscribe(self, *topics, **kwargs):
        """
        Client unsubscribe handler.
        """
        if not topics:
            topics = self.topics

        for topic in topics:
            super().unsubscribe(topic, **kwargs)
            self.topics.remove(topic)

    def connect_hndl(self):
        def handler(*_, **__):
            self.subscribe()

        return handler

    def run(self):
        super().run()
        self.connect(host=self.host, port=self.port, keepalive=self.keepalive)
        self._running = True
        self.loop_forever()

    def stop(self):
        if not self.is_alive():
            return

        self._stop_scheduled = True
        self.disconnect()
        self._running = False


class MqttBackend(Backend):
    """
    Backend that reads messages from a configured MQTT topic (default:
    ``platypush_bus_mq/<device_id>``) and posts them to the application bus.

    Triggers:

        * :class:`platypush.message.event.mqtt.MQTTMessageEvent` when a new
            message is received on one of the custom listeners

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)
    """

    _default_mqtt_port = 1883

    def __init__(
        self,
        *args,
        host: Optional[str] = None,
        port: int = _default_mqtt_port,
        topic: str = 'platypush_bus_mq',
        subscribe_default_topic: bool = True,
        tls_cafile: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version: Optional[str] = None,
        tls_ciphers: Optional[str] = None,
        tls_insecure: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        listeners=None,
        **kwargs,
    ):
        """
        :param host: MQTT broker host. If no host configuration is specified then
            the backend will use the host configuration specified on the ``mqtt``
            plugin if it's available.
        :param port: MQTT broker port (default: 1883)
        :param topic: Topic to read messages from (default: ``platypush_bus_mq/<device_id>``)
        :param subscribe_default_topic: Whether the backend should subscribe the default topic (default:
            ``platypush_bus_mq/<device_id>``) and execute the messages received there as action requests
            (default: True).
        :param tls_cafile: If TLS/SSL is enabled on the MQTT server and the certificate requires a certificate authority
            to authenticate it, `ssl_cafile` will point to the provided ca.crt file (default: None)
        :param tls_certfile: If TLS/SSL is enabled on the MQTT server and a client certificate it required, specify it
            here (default: None)
        :param tls_keyfile: If TLS/SSL is enabled on the MQTT server and a client certificate key it required,
            specify it here (default: None) :type tls_keyfile: str
        :param tls_version: If TLS/SSL is enabled on the MQTT server and it requires a certain TLS version, specify it
            here (default: None). Supported versions: ``tls`` (automatic), ``tlsv1``, ``tlsv1.1``, ``tlsv1.2``.
        :param tls_ciphers: If TLS/SSL is enabled on the MQTT server and an explicit list of supported ciphers is
            required, specify it here (default: None)
        :param tls_insecure: Set to True to ignore TLS insecure warnings (default: False).
        :param username: Specify it if the MQTT server requires authentication (default: None)
        :param password: Specify it if the MQTT server requires authentication (default: None)
        :param client_id: ID used to identify the client on the MQTT server (default: None).
            If None is specified then ``Config.get('device_id')`` will be used.
        :param listeners: If specified then the MQTT backend will also listen for
            messages on the additional configured message queues. This parameter
            is a list of maps where each item supports the same arguments passed
            to the main backend configuration (host, port, topic, password etc.).
            Note that the message queue configured on the main configuration
            will expect valid Platypush messages that then can execute, while
            message queues registered to the listeners will accept any message. Example::

                listeners:
                    - host: localhost
                      topics:
                          - topic1
                          - topic2
                          - topic3
                    - host: sensors
                      topics:
                          - topic4
                          - topic5

        """

        super().__init__(*args, **kwargs)

        if host:
            self.host = host
            self.port = port
            self.tls_cafile = self._expandpath(tls_cafile) if tls_cafile else None
            self.tls_certfile = self._expandpath(tls_certfile) if tls_certfile else None
            self.tls_keyfile = self._expandpath(tls_keyfile) if tls_keyfile else None
            self.tls_version = MQTTPlugin.get_tls_version(tls_version)
            self.tls_ciphers = tls_ciphers
            self.tls_insecure = tls_insecure
            self.username = username
            self.password = password
            self.client_id: str = client_id or Config.get('device_id')
        else:
            client = get_plugin('mqtt')
            assert (
                client.host
            ), 'No host specified on backend.mqtt nor mqtt configuration'

            self.host = client.host
            self.port = client.port
            self.tls_cafile = client.tls_cafile
            self.tls_certfile = client.tls_certfile
            self.tls_keyfile = client.tls_keyfile
            self.tls_version = client.tls_version
            self.tls_ciphers = client.tls_ciphers
            self.tls_insecure = client.tls_insecure
            self.username = client.username
            self.password = client.password
            self.client_id = client_id or client.client_id

        self.topic = f'{topic}/{self.device_id}'
        self.subscribe_default_topic = subscribe_default_topic
        self._listeners: Dict[str, MqttClient] = {}  # client_id -> MqttClient map
        self.listeners_conf = listeners or []

    def send_message(self, msg, *_, topic: Optional[str] = None, **kwargs):
        try:
            client = get_plugin('mqtt')
            client.send_message(
                topic=topic or self.topic,
                msg=msg,
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                tls_cafile=self.tls_cafile,
                tls_certfile=self.tls_certfile,
                tls_keyfile=self.tls_keyfile,
                tls_version=self.tls_version,
                tls_insecure=self.tls_insecure,
                tls_ciphers=self.tls_ciphers,
                **kwargs,
            )
        except Exception as e:
            self.logger.exception(e)

    @staticmethod
    def _expandpath(path: str) -> str:
        return os.path.abspath(os.path.expanduser(path)) if path else path

    def add_listeners(self, *listeners):
        for i, listener in enumerate(listeners):
            host = listener.get('host', self.host)
            port = listener.get('port', self.port)
            username = listener.get('username', self.username)
            password = listener.get('password', self.password)
            tls_cafile = self._expandpath(listener.get('tls_cafile', self.tls_cafile))
            tls_certfile = self._expandpath(
                listener.get('tls_certfile', self.tls_certfile)
            )
            tls_keyfile = self._expandpath(
                listener.get('tls_keyfile', self.tls_keyfile)
            )
            tls_version = MQTTPlugin.get_tls_version(
                listener.get('tls_version', self.tls_version)
            )
            tls_ciphers = listener.get('tls_ciphers', self.tls_ciphers)
            tls_insecure = listener.get('tls_insecure', self.tls_insecure)
            topics = listener.get('topics')

            if not topics:
                self.logger.warning(
                    'No list of topics specified for listener n.%d', i + 1
                )
                continue

            client = self._get_client(
                host=host,
                port=port,
                topics=topics,
                username=username,
                password=password,
                client_id=self.client_id,
                tls_cafile=tls_cafile,
                tls_certfile=tls_certfile,
                tls_keyfile=tls_keyfile,
                tls_version=tls_version,
                tls_ciphers=tls_ciphers,
                tls_insecure=tls_insecure,
            )

            if not client.is_alive():
                client.start()

    def _get_client_id(
        self,
        host: str,
        port: int,
        topics: Optional[List[str]] = None,
        client_id: Optional[str] = None,
        on_message: Optional[Callable[[MqttClient, Any, mqtt.MQTTMessage], Any]] = None,
    ) -> str:
        client_id = client_id or self.client_id
        client_hash = hashlib.sha1(
            '|'.join(
                [
                    host,
                    str(port),
                    json.dumps(sorted(topics or [])),
                    str(id(on_message)),
                ]
            ).encode()
        ).hexdigest()

        return f'{client_id}-{client_hash}'

    def _get_client(
        self,
        host: str,
        port: int,
        topics: Optional[List[str]] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        tls_cafile: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version=None,
        tls_ciphers=None,
        tls_insecure: bool = False,
        on_message: Optional[Callable] = None,
    ) -> MqttClient:
        on_message = on_message or self.on_mqtt_message()
        client_id = self._get_client_id(
            host=host,
            port=port,
            topics=topics,
            client_id=client_id,
            on_message=on_message,
        )
        client = self._listeners.get(client_id)

        if not (client and client.is_alive()):
            client = self._listeners[client_id] = MqttClient(
                host=host,
                port=port,
                topics=topics,
                username=username,
                password=password,
                client_id=client_id,
                tls_cafile=tls_cafile,
                tls_certfile=tls_certfile,
                tls_keyfile=tls_keyfile,
                tls_version=tls_version,
                tls_ciphers=tls_ciphers,
                tls_insecure=tls_insecure,
                on_message=on_message,
            )

        if topics:
            client.subscribe(*topics)

        return client

    def on_mqtt_message(self):
        def handler(client: MqttClient, _, msg: mqtt.MQTTMessage):
            data = msg.payload
            try:
                data = data.decode('utf-8')
                data = json.loads(data)
            except Exception as e:
                self.logger.debug(str(e))

            self.bus.post(
                MQTTMessageEvent(
                    host=client.host, port=client.port, topic=msg.topic, msg=data
                )
            )

        return handler

    def on_exec_message(self):
        def handler(_, __, msg: mqtt.MQTTMessage):
            def response_thread(msg):
                response = self.get_message_response(msg)
                if not response:
                    return
                response_topic = f'{self.topic}/responses/{msg.id}'

                self.logger.info(
                    'Processing response on the MQTT topic %s: %s',
                    response_topic,
                    response,
                )

                self.send_message(response, topic=response_topic)

            msg = msg.payload.decode('utf-8')
            try:
                msg = json.loads(msg)
                msg = Message.build(msg)
            except Exception as e:
                self.logger.debug(str(e))

            if not msg:
                return

            self.logger.info('Received message on the MQTT backend: %s', msg)

            try:
                self.on_message(msg)
            except Exception as e:
                self.logger.exception(e)
                return

            if isinstance(msg, Request):
                threading.Thread(
                    target=response_thread,
                    name='MQTTProcessorResponseThread',
                    args=(msg,),
                ).start()

        return handler

    def run(self):
        super().run()

        if self.host and self.subscribe_default_topic:
            topics = [self.topic]
            client = self._get_client(
                host=self.host,
                port=self.port,
                topics=topics,
                username=self.username,
                password=self.password,
                client_id=self.client_id,
                tls_cafile=self.tls_cafile,
                tls_certfile=self.tls_certfile,
                tls_keyfile=self.tls_keyfile,
                tls_version=self.tls_version,
                tls_ciphers=self.tls_ciphers,
                tls_insecure=self.tls_insecure,
                on_message=self.on_exec_message(),
            )

            client.start()
            self.logger.info(
                'Initialized MQTT backend on host %s:%d, topic=%s',
                self.host,
                self.port,
                self.topic,
            )

        self.add_listeners(*self.listeners_conf)

    def on_stop(self):
        self.logger.info('Received STOP event on the MQTT backend')

        for listener in self._listeners.values():
            try:
                listener.stop()
            except Exception as e:
                self.logger.warning('Could not stop MQTT listener: %s', e)

        self.logger.info('MQTT backend terminated')


# vim:sw=4:ts=4:et:
