import json
import paho.mqtt.publish as publisher

from platypush.message import Message
from platypush.plugins import Plugin, action


class MqttPlugin(Plugin):
    """
    This plugin allows you to send custom message to a message queue compatible
    with the MQTT protocol, see http://mqtt.org/
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def send_message(self, topic, msg, host, port=1883, tls_cafile=None,
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

        publisher_args = {
            'hostname': host,
            'port': port,
        }

        if username and password:
            publisher_args['auth'] = {
                'username': username,
                'password': password,
            }

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

        try: msg = json.dumps(msg)
        except: pass

        try: msg = Message.build(json.loads(msg))
        except: pass

        publisher.single(topic, str(msg), **publisher_args)


# vim:sw=4:ts=4:et:

