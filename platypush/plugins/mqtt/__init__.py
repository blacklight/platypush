import io
import json
import os
import threading

from typing import Any, Optional, IO

from platypush.config import Config
from platypush.message import Message
from platypush.plugins import Plugin, action


class MqttPlugin(Plugin):
    """
    This plugin allows you to send custom message to a message queue compatible
    with the MQTT protocol, see https://mqtt.org/

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)

    """

    def __init__(
        self,
        host=None,
        port=1883,
        tls_cafile=None,
        tls_certfile=None,
        tls_keyfile=None,
        tls_version=None,
        tls_ciphers=None,
        tls_insecure=False,
        username=None,
        password=None,
        client_id=None,
        timeout=None,
        **kwargs,
    ):
        """
        :param host: If set, MQTT messages will by default routed to this host
            unless overridden in `send_message` (default: None)
        :type host: str

        :param port: If a default host is set, specify the listen port
            (default: 1883)
        :type port: int

        :param tls_cafile: If a default host is set and requires TLS/SSL,
            specify the certificate authority file (default: None)
        :type tls_cafile: str

        :param tls_certfile: If a default host is set and requires TLS/SSL,
            specify the certificate file (default: None)
        :type tls_certfile: str

        :param tls_keyfile: If a default host is set and requires TLS/SSL,
            specify the key file (default: None)
        :type tls_keyfile: str

        :param tls_version: If TLS/SSL is enabled on the MQTT server and it
            requires a certain TLS version, specify it here (default: None).
            Supported versions: ``tls`` (automatic), ``tlsv1``, ``tlsv1.1``,
            ``tlsv1.2``.
        :type tls_version: str

        :param tls_ciphers: If a default host is set and requires TLS/SSL,
            specify the supported ciphers (default: None)
        :type tls_ciphers: str

        :param tls_insecure: Set to True to ignore TLS insecure warnings
            (default: False).
        :type tls_insecure: bool

        :param username: If a default host is set and requires user
            authentication, specify the username ciphers (default: None)
        :type username: str

        :param password: If a default host is set and requires user
            authentication, specify the password ciphers (default: None)
        :type password: str

        :param client_id: ID used to identify the client on the MQTT server
            (default: None). If None is specified then
            ``Config.get('device_id')`` will be used.
        :type client_id: str

        :param timeout: Client timeout in seconds (default: None).
        :type timeout: int
        """

        super().__init__(**kwargs)

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id or Config.get('device_id')
        self.tls_cafile = self._expandpath(tls_cafile) if tls_cafile else None
        self.tls_certfile = self._expandpath(tls_certfile) if tls_certfile else None
        self.tls_keyfile = self._expandpath(tls_keyfile) if tls_keyfile else None
        self.tls_version = self.get_tls_version(tls_version)
        self.tls_insecure = tls_insecure
        self.tls_ciphers = tls_ciphers
        self.timeout = timeout

    @staticmethod
    def get_tls_version(version: Optional[str] = None):
        import ssl

        if not version:
            return None

        if isinstance(version, type(ssl.PROTOCOL_TLS)):
            return version

        if isinstance(version, str):
            version = version.lower()

        if version == 'tls':
            return ssl.PROTOCOL_TLS
        if version == 'tlsv1':
            return ssl.PROTOCOL_TLSv1
        if version == 'tlsv1.1':
            return ssl.PROTOCOL_TLSv1_1
        if version == 'tlsv1.2':
            return ssl.PROTOCOL_TLSv1_2

        assert f'Unrecognized TLS version: {version}'

    def _mqtt_args(self, **kwargs):
        return {
            'host': kwargs.get('host', self.host),
            'port': kwargs.get('port', self.port),
            'timeout': kwargs.get('timeout', self.timeout),
            'tls_certfile': kwargs.get('tls_certfile', self.tls_certfile),
            'tls_keyfile': kwargs.get('tls_keyfile', self.tls_keyfile),
            'tls_version': kwargs.get('tls_version', self.tls_version),
            'tls_ciphers': kwargs.get('tls_ciphers', self.tls_ciphers),
            'username': kwargs.get('username', self.username),
            'password': kwargs.get('password', self.password),
        }

    @staticmethod
    def _expandpath(path: Optional[str] = None) -> Optional[str]:
        return os.path.abspath(os.path.expanduser(path)) if path else None

    def _get_client(
        self,
        tls_cafile: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version: Optional[str] = None,
        tls_ciphers: Optional[str] = None,
        tls_insecure: Optional[bool] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        from paho.mqtt.client import Client

        tls_cafile = self._expandpath(tls_cafile or self.tls_cafile)
        tls_certfile = self._expandpath(tls_certfile or self.tls_certfile)
        tls_keyfile = self._expandpath(tls_keyfile or self.tls_keyfile)
        tls_ciphers = tls_ciphers or self.tls_ciphers
        username = username or self.username
        password = password or self.password

        tls_version = tls_version or self.tls_version  # type: ignore[reportGeneralTypeIssues]
        if tls_version:
            tls_version = self.get_tls_version(tls_version)  # type: ignore[reportGeneralTypeIssues]
        if tls_insecure is None:
            tls_insecure = self.tls_insecure

        client = Client()

        if username and password:
            client.username_pw_set(username, password)
        if tls_cafile:
            client.tls_set(
                ca_certs=tls_cafile,
                certfile=tls_certfile,
                keyfile=tls_keyfile,
                tls_version=tls_version,  # type: ignore[reportGeneralTypeIssues]
                ciphers=tls_ciphers,
            )

            client.tls_insecure_set(tls_insecure)

        return client

    @action
    def publish(
        self,
        topic: str,
        msg: Any,
        host: Optional[str] = None,
        port: Optional[int] = None,
        reply_topic: Optional[str] = None,
        timeout: int = 60,
        tls_cafile: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version: Optional[str] = None,
        tls_ciphers: Optional[str] = None,
        tls_insecure: Optional[bool] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        qos: int = 0,
    ):
        """
        Sends a message to a topic.

        :param topic: Topic/channel where the message will be delivered
        :param msg: Message to be sent. It can be a list, a dict, or a Message
            object.
        :param host: MQTT broker hostname/IP (default: default host configured
            on the plugin).
        :param port: MQTT broker port (default: default port configured on the
            plugin).
        :param reply_topic: If a ``reply_topic`` is specified, then the action
            will wait for a response on this topic.
        :param timeout: If ``reply_topic`` is set, use this parameter to
            specify the maximum amount of time to wait for a response (default:
            60 seconds).
        :param tls_cafile: If TLS/SSL is enabled on the MQTT server and the
            certificate requires a certificate authority to authenticate it,
            `ssl_cafile` will point to the provided ca.crt file (default:
            None).
        :param tls_certfile: If TLS/SSL is enabled on the MQTT server and a
            client certificate it required, specify it here (default: None).
        :param tls_keyfile: If TLS/SSL is enabled on the MQTT server and a
            client certificate key it required, specify it here (default:
            None).
        :param tls_version: If TLS/SSL is enabled on the MQTT server and it
            requires a certain TLS version, specify it here (default: None).
            Supported versions: ``tls`` (automatic), ``tlsv1``, ``tlsv1.1``,
            ``tlsv1.2``.
        :param tls_insecure: Set to True to ignore TLS insecure warnings
            (default: False).
        :param tls_ciphers: If TLS/SSL is enabled on the MQTT server and an
            explicit list of supported ciphers is required, specify it here
            (default: None).
        :param username: Specify it if the MQTT server requires authentication
            (default: None).
        :param password: Specify it if the MQTT server requires authentication
            (default: None).
        :param qos: Quality of Service (_QoS_) for the message - see `MQTT QoS
            <https://assetwolf.com/learn/mqtt-qos-understanding-quality-of-service>`_
            (default: 0).
        """
        response_buffer = io.BytesIO()
        client = None

        try:
            # Try to parse it as a platypush message or dump it to JSON from a dict/list
            if isinstance(msg, (dict, list)):
                msg = json.dumps(msg)

                try:
                    msg = Message.build(json.loads(msg))
                except Exception as e:
                    self.logger.debug('Not a valid JSON: %s', e)

            host = host or self.host
            port = port or self.port or 1883
            assert host, 'No host specified'

            client = self._get_client(
                tls_cafile=tls_cafile,
                tls_certfile=tls_certfile,
                tls_keyfile=tls_keyfile,
                tls_version=tls_version,
                tls_ciphers=tls_ciphers,
                tls_insecure=tls_insecure,
                username=username,
                password=password,
            )

            client.connect(host, port, keepalive=timeout)
            response_received = threading.Event()

            if reply_topic:
                client.on_message = self._response_callback(
                    reply_topic=reply_topic,
                    event=response_received,
                    buffer=response_buffer,
                )
                client.subscribe(reply_topic)

            client.publish(topic, str(msg), qos=qos)
            if not reply_topic:
                return

            client.loop_start()
            ok = response_received.wait(timeout=timeout)
            if not ok:
                raise TimeoutError('Response timed out')
            return response_buffer.getvalue()
        finally:
            response_buffer.close()

            if client:
                try:
                    client.loop_stop()
                except Exception as e:
                    self.logger.warning('Could not stop client loop: %s', e)

                client.disconnect()

    @staticmethod
    def _response_callback(reply_topic: str, event: threading.Event, buffer: IO[bytes]):
        def on_message(client, _, msg):
            if msg.topic != reply_topic:
                return

            buffer.write(msg.payload)
            client.loop_stop()
            event.set()

        return on_message

    @action
    def send_message(self, *args, **kwargs):
        """
        Alias for :meth:`platypush.plugins.mqtt.MqttPlugin.publish`.
        """
        return self.publish(*args, **kwargs)


# vim:sw=4:ts=4:et:
