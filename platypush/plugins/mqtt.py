import json
import os
import paho.mqtt.publish as publisher

from platypush.message import Message
from platypush.plugins import Plugin, action


class MqttPlugin(Plugin):
    """
    This plugin allows you to send custom message to a message queue compatible
    with the MQTT protocol, see http://mqtt.org/
    """

    def __init__(self, host=None, port=1883, tls_cafile=None,
                 tls_certfile=None, tls_keyfile=None,
                 tls_version=None, tls_ciphers=None, username=None,
                 password=None, *args, **kwargs):
        """
        :param host: If set, MQTT messages will by default routed to this host unless overridden in `send_message` (default: None)
        :type host: str

        :param port: If a default host is set, specify the listen port (default: 1883)
        :type port: int

        :param tls_cafile: If a default host is set and requires TLS/SSL, specify the certificate authority file (default: None)
        :type tls_cafile: str

        :param tls_certfile: If a default host is set and requires TLS/SSL, specify the certificate file (default: None)
        :type tls_certfile: str

        :param tls_keyfile: If a default host is set and requires TLS/SSL, specify the key file (default: None)
        :type tls_keyfile: str

        :param tls_version: If a default host is set and requires TLS/SSL, specify the minimum TLS supported version (default: None)
        :type tls_version: str

        :param tls_ciphers: If a default host is set and requires TLS/SSL, specify the supported ciphers (default: None)
        :type tls_ciphers: str

        :param username: If a default host is set and requires user authentication, specify the username ciphers (default: None)
        :type username: str

        :param password: If a default host is set and requires user authentication, specify the password ciphers (default: None)
        :type password: str
        """

        super().__init__(*args, **kwargs)

        self.host = host
        self.port = port
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


    @action
    def send_message(self, topic, msg, host=None, port=1883, tls_cafile=None,
                     tls_certfile=None, tls_keyfile=None,
                     tls_version=None, tls_ciphers=None, username=None,
                     password=None, *args, **kwargs):
        """
        Sends a message to a topic/channel.

        :param topic: Topic/channel where the message will be delivered
        :type topic: str

        :param msg: Message to be sent. It can be a list, a dict, or a Message object

        :param host: MQTT broker hostname/IP
        :type host: str

        :param port: MQTT broker port (default: 1883)
        :type port: int

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

        if not host and not self.host:
            raise RuntimeError('No host specified and no default host configured')

        publisher_args = {
            'hostname': host or self.host,
            'port': port or self.port,
        }

        if host:
            if username and password:
                publisher_args['auth'] = {
                    'username': username,
                    'password': password,
                }
        else:
            if self.username and self.password:
                publisher_args['auth'] = {
                    'username': username,
                    'password': password,
                }

        if host:
            if tls_cafile:
                publisher_args['tls'] = { 'ca_certs': tls_cafile }
                if tls_certfile:
                    publishers_args['tls']['certfile'] = tls_certfile
                if tls_keyfile:
                    publishers_args['tls']['keyfile'] = tls_keyfile
                if tls_version:
                    publishers_args['tls']['tls_version'] = tls_version
                if tls_ciphers:
                    publishers_args['tls']['ciphers'] = tls_ciphers
        else:
            if self.tls_cafile:
                publisher_args['tls'] = { 'ca_certs': self.tls_cafile }
                if self.tls_certfile:
                    publishers_args['tls']['certfile'] = self.tls_certfile
                if self.tls_keyfile:
                    publishers_args['tls']['keyfile'] = self.tls_keyfile
                if self.tls_version:
                    publishers_args['tls']['tls_version'] = self.tls_version
                if self.tls_ciphers:
                    publishers_args['tls']['ciphers'] = self.tls_ciphers

        try: msg = json.dumps(msg)
        except: pass

        try: msg = Message.build(json.loads(msg))
        except: pass

        publisher.single(topic, str(msg), **publisher_args)


# vim:sw=4:ts=4:et:

