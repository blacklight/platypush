import json
import os
import threading

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

    def __init__(self, host, port=_default_mqtt_port, topic='platypush_bus_mq',
                 tls_cafile=None, tls_certfile=None, tls_keyfile=None,
                 tls_version=None, tls_ciphers=None, username=None,
                 password=None, listeners=None, *args, **kwargs):
        """
        :param host: MQTT broker host
        :type host: str

        :param port: MQTT broker port (default: 1883)
        :type port: int

        :param topic: Topic to read messages from (default: ``platypush_bus_mq/<device_id>``)
        :type topic: str

        :param tls_cafile: If TLS/SSL is enabled on the MQTT server and the certificate requires a certificate authority to authenticate it, `ssl_cafile` will point to the provided ca.crt file (default: None)
        :type tls_cafile: str

        :param tls_certfile: If TLS/SSL is enabled on the MQTT server and a client certificate it required, specify it here (default: None)
        :type tls_certfile: str

        :param tls_keyfile: If TLS/SSL is enabled on the MQTT server and a client certificate key it required, specify it here (default: None)
        :type tls_keyfile: str

        :param tls_version: If TLS/SSL is enabled on the MQTT server and it requires a certain TLS version, specify it here (default: None)
        :type tls_version: str

        :param tls_ciphers: If TLS/SSL is enabled on the MQTT server and an explicit list of supported ciphers is required, specify it here (default: None)
        :type tls_ciphers: str

        :param username: Specify it if the MQTT server requires authentication (default: None)
        :type username: str

        :param password: Specify it if the MQTT server requires authentication (default: None)
        :type password: str

        :param listeners: If specified then the MQTT backend will also listen for
            messages on the additional configured message queues. This parameter
            is a list of maps where each item supports the same arguments passed
            to the main backend configuration (host, port, topic, password etc.).
            Note that the message queue configured on the main configuration
            will expect valid Platypush messages that then can execute, while
            message queues registered to the listeners will accept any message.
        :type listeners: list[dict]
        """

        super().__init__(*args, **kwargs)

        self.host = host
        self.port = port
        self.topic = '{}/{}'.format(topic, self.device_id)
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


    def send_message(self, msg):
        try:
            client = get_plugin('mqtt')
            client.send_message(topic=self.topic, msg=msg, host=self.host,
                                port=self.port, username=self.username,
                                password=self.password, tls_cafile=self.tls_cafile,
                                tls_certfile=self.tls_certfile,
                                tls_keyfile=self.tls_keyfile,
                                tls_version=self.tls_version,
                                tls_ciphers=self.tls_ciphers)
        except Exception as e:
            self.logger.exception(e)

    def _initialize_listeners(self, listeners_conf):
        import paho.mqtt.client as mqtt

        def listener_thread(client, host, port):
            client.connect(host, port, 60)
            client.loop_forever()

        def on_connect(topics):
            def handler(client, userdata, flags, rc):
                for topic in topics:
                    client.subscribe(topic)
            return handler

        def on_message(client, userdata, msg):
            data = msg.payload
            try:
                data = data.decode('utf-8')
                data = json.loads(data)
            except:
                pass

            self.bus.post(MQTTMessageEvent(host=client._host, port=client._port,
                                           topic=msg.topic, msg=data))

        for i, listener in enumerate(listeners_conf):
            host = listener.get('host')
            port = listener.get('port', self._default_mqtt_port)
            topics = listener.get('topics')
            username = listener.get('username')
            password = listener.get('password')
            tls_cafile = listener.get('tls_cafile')

            if not host or not topics:
                self.logger.warning('No host nor list of topics specified for ' +
                                    'listener n.{}'.format(i+1))
                continue

            client = mqtt.Client()
            client.on_connect = on_connect(topics)
            client.on_message = on_message

            if username and password:
                client.username_pw_set(username, password)

            if tls_cafile:
                client.tls_set(ca_certs=tls_cafile,
                               certfile=listener.get('tls_certfile'),
                               keyfile=listener.get('tls_keyfile'),
                               tls_version=listener.get('tls_version'),
                               ciphers=listener.get('tls_ciphers'))

            threading.Thread(target=listener_thread, kwargs = {
                'client': client, 'host': host, 'port': port }).start()


    def run(self):
        def on_connect(client, userdata, flags, rc):
            client.subscribe(self.topic)

        def on_message(client, userdata, msg):
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
            try: msg = Message.build(json.loads(msg))
            except: pass
            if not msg: return

            self.logger.info('Received message on the MQTT backend: {}'.format(msg))

            try:
                self.on_message(msg)
            except Exception as e:
                self.logger.exception(e)
                return

            if isinstance(msg, Request):
                threading.Thread(target=response_thread,
                                 name='MQTTProcessor',
                                 args=(msg,)).start()

        import paho.mqtt.client as mqtt

        super().run()
        self._client = mqtt.Client()
        self._client.on_connect = on_connect
        self._client.on_message = on_message

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
                self.logger.warning('Could not stop listener ' +
                                    '{host}:{port}: {error}'.format(
                                        host=listener._host, port=listener._port,
                                        error=str(e)))


# vim:sw=4:ts=4:et:
