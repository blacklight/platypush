import json
import os
import threading
from typing import Optional

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message import Message
from platypush.message.event.mqtt import MQTTMessageEvent
from platypush.message.request import Request
from platypush.utils import set_thread_name


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

    def __init__(self, host: Optional[str] = None, port: int = _default_mqtt_port,
                 topic='platypush_bus_mq', subscribe_default_topic: bool = True,
                 tls_cafile: Optional[str] = None, tls_certfile: Optional[str] = None,
                 tls_keyfile: Optional[str] = None, tls_version: Optional[str] = None,
                 tls_ciphers: Optional[str] = None, username: Optional[str] = None,
                 password: Optional[str] = None, listeners=None, *args, **kwargs):
        """
        :param host: MQTT broker host
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
            here (default: None)
        :param tls_ciphers: If TLS/SSL is enabled on the MQTT server and an explicit list of supported ciphers is
            required, specify it here (default: None)
        :param username: Specify it if the MQTT server requires authentication (default: None)
        :param password: Specify it if the MQTT server requires authentication (default: None)
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

        self.host = host
        self.port = port
        self.topic = '{}/{}'.format(topic, self.device_id)
        self.subscribe_default_topic = subscribe_default_topic
        self.username = username
        self.password = password
        self._client = None
        self._listeners = []

        self.tls_cafile = os.path.abspath(os.path.expanduser(tls_cafile)) \
            if tls_cafile else None

        self.tls_certfile = os.path.abspath(os.path.expanduser(tls_certfile)) \
            if tls_certfile else None

        self.tls_keyfile = os.path.abspath(os.path.expanduser(tls_keyfile)) \
            if tls_keyfile else None

        self.tls_version = tls_version
        self.tls_ciphers = tls_ciphers
        self.listeners_conf = listeners or []

    def send_message(self, msg, topic: Optional[str] = None, **kwargs):
        try:
            client = get_plugin('mqtt')
            client.send_message(topic=topic or self.topic, msg=msg, host=self.host,
                                port=self.port, username=self.username,
                                password=self.password, tls_cafile=self.tls_cafile,
                                tls_certfile=self.tls_certfile,
                                tls_keyfile=self.tls_keyfile,
                                tls_version=self.tls_version,
                                tls_ciphers=self.tls_ciphers, **kwargs)
        except Exception as e:
            self.logger.exception(e)

    @staticmethod
    def on_connect(*topics):
        # noinspection PyUnusedLocal
        def handler(client, userdata, flags, rc):
            for topic in topics:
                client.subscribe(topic)

        return handler

    def on_mqtt_message(self):
        def handler(client, _, msg):
            data = msg.payload
            # noinspection PyBroadException
            try:
                data = data.decode('utf-8')
                data = json.loads(data)
            except:
                pass

            # noinspection PyProtectedMember
            self.bus.post(MQTTMessageEvent(host=client._host, port=client._port, topic=msg.topic, msg=data))

        return handler

    def _initialize_listeners(self, listeners_conf):
        import paho.mqtt.client as mqtt

        # noinspection PyShadowingNames
        def listener_thread(client, host, port):
            client.connect(host, port)
            client.loop_forever()

        # noinspection PyShadowingNames,PyUnusedLocal
        for i, listener in enumerate(listeners_conf):
            host = listener.get('host')
            port = listener.get('port', self._default_mqtt_port)
            topics = listener.get('topics')
            username = listener.get('username')
            password = listener.get('password')
            tls_cafile = listener.get('tls_cafile')

            if not host or not topics:
                self.logger.warning('No host nor list of topics specified for ' +
                                    'listener n.{}'.format(i + 1))
                continue

            client = mqtt.Client()
            client.on_connect = self.on_connect(*topics)
            client.on_message = self.on_mqtt_message()

            if username and password:
                client.username_pw_set(username, password)

            if tls_cafile:
                client.tls_set(ca_certs=tls_cafile,
                               certfile=listener.get('tls_certfile'),
                               keyfile=listener.get('tls_keyfile'),
                               tls_version=listener.get('tls_version'),
                               ciphers=listener.get('tls_ciphers'))

            threading.Thread(target=listener_thread, kwargs={
                'client': client, 'host': host, 'port': port}).start()

    def on_exec_message(self):
        def handler(_, __, msg):
            # noinspection PyShadowingNames
            def response_thread(msg):
                set_thread_name('MQTTProcessor')
                response = self.get_message_response(msg)
                if not response:
                    return
                response_topic = '{}/responses/{}'.format(self.topic, msg.id)

                self.logger.info('Processing response on the MQTT topic {}: {}'.
                                 format(response_topic, response))

                self.send_message(response)

            msg = msg.payload.decode('utf-8')
            # noinspection PyBroadException
            try:
                msg = json.loads(msg)
                msg = Message.build(msg)
            except:
                pass

            if not msg:
                return

            self.logger.info('Received message on the MQTT backend: {}'.format(msg))

            try:
                self.on_message(msg)
            except Exception as e:
                self.logger.exception(e)
                return

            if isinstance(msg, Request):
                threading.Thread(target=response_thread, name='MQTTProcessor', args=(msg,)).start()

        return handler

    def run(self):
        import paho.mqtt.client as mqtt

        super().run()
        self._client = None

        if self.host:
            self._client = mqtt.Client()
            if self.subscribe_default_topic:
                self._client.on_connect = self.on_connect(self.topic)

            self._client.on_message = self.on_exec_message()
            if self.username and self.password:
                self._client.username_pw_set(self.username, self.password)

            if self.tls_cafile:
                self._client.tls_set(ca_certs=self.tls_cafile, certfile=self.tls_certfile,
                                     keyfile=self.tls_keyfile, tls_version=self.tls_version,
                                     ciphers=self.tls_ciphers)

            self._client.connect(self.host, self.port, 60)
            self.logger.info('Initialized MQTT backend on host {}:{}, topic {}'.
                             format(self.host, self.port, self.topic))

        self._initialize_listeners(self.listeners_conf)
        if self._client:
            self._client.loop_forever()

    def stop(self):
        self.logger.info('Received STOP event on MqttBackend')
        if self._client:
            self._client.disconnect()
            self._client.loop_stop()
            self._client = None

        for listener in self._listeners:
            try:
                listener.loop_stop()
            except Exception as e:
                # noinspection PyProtectedMember
                self.logger.warning('Could not stop listener {host}:{port}: {error}'.format(
                    host=listener._host, port=listener._port,
                    error=str(e)))


# vim:sw=4:ts=4:et:
