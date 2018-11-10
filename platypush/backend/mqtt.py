import json
import os
import threading

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message import Message
from platypush.message.request import Request


class MqttBackend(Backend):
    """
    Backend that reads messages from a configured MQTT topic (default:
    ``platypush_bus_mq/<device_id>``) and posts them to the application bus.

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)
    """

    def __init__(self, host, port=1883, topic='platypush_bus_mq', tls_cafile=None,
                 tls_certfile=None, tls_keyfile=None,
                 tls_version=None, tls_ciphers=None, username=None,
                 password=None, *args, **kwargs):
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
        """

        super().__init__(*args, **kwargs)

        self.host = host
        self.port = port
        self.topic = '{}/{}'.format(topic, self.device_id)
        self.username = username
        self.password = password

        self.tls_cafile = os.path.abspath(os.path.expanduser(tls_cafile)) \
            if tls_cafile else None

        self.tls_certfile = os.path.abspath(os.path.expanduser(tls_certfile)) \
            if tls_certfile else None

        self.tls_keyfile = os.path.abspath(os.path.expanduser(tls_keyfile)) \
            if tls_keyfile else None

        self.tls_version = tls_version
        self.tls_ciphers = tls_ciphers


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

    def run(self):
        def on_connect(client, userdata, flags, rc):
            client.subscribe(self.topic)

        def on_message(client, userdata, msg):
            def response_thread(msg):
                response = self.get_message_response(msg)
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
                threading.Thread(target=response_thread, args=(msg,)).start()

        super().run()
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        if self.username and self.password:
            client.username_pw_set(self.username, self.password)

        if self.tls_cafile:
            client.tls_set(ca_certs=self.tls_cafile, certfile=self.tls_certfile,
                           keyfile=self.tls_keyfile, tls_version=self.tls_version,
                           ciphers=self.tls_ciphers)

        client.connect(self.host, self.port, 60)
        self.logger.info('Initialized MQTT backend on host {}:{}, topic {}'.
                     format(self.host, self.port, self.topic))

        client.loop_forever()


# vim:sw=4:ts=4:et:

