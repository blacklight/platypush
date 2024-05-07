from enum import IntEnum
import logging
import os
import threading
from typing import Any, Callable, Dict, Iterable, Optional, Union

import paho.mqtt.client as mqtt

from platypush.config import Config

MqttCallback = Callable[["MqttClient", Any, mqtt.MQTTMessage], Any]
DEFAULT_TIMEOUT: int = 30


class MqttClient(mqtt.Client, threading.Thread):
    """
    Wrapper class for an MQTT client executed in a separate thread.
    """

    def __init__(
        self,
        *args,
        host: str,
        port: int,
        client_id: str,
        topics: Iterable[str] = (),
        on_message: Optional[MqttCallback] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        tls_cafile: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version: Optional[Union[str, IntEnum]] = None,
        tls_ciphers: Optional[str] = None,
        tls_insecure: bool = False,
        timeout: int = DEFAULT_TIMEOUT,
        **kwargs,
    ):
        self.client_id = client_id or str(Config.get('device_id'))
        kwargs['client_id'] = self.client_id

        # Breaking change in paho.mqtt >= 2.0.0: the callback API version
        # parameter should be passed, see
        # https://github.com/eclipse/paho.mqtt.python/blob/28aa2e6b26a86e4b29126323892fb5f43637d6d6/ChangeLog.txt#L6
        cbApiVersion = getattr(mqtt, 'CallbackAPIVersion', None)
        if cbApiVersion:
            kwargs['callback_api_version'] = cbApiVersion.VERSION1

        mqtt.Client.__init__(self, *args, **kwargs)

        threading.Thread.__init__(self, name=f'MQTTClient:{self.client_id}')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = host
        self.port = port
        self.tls_cafile = self._expandpath(tls_cafile)
        self.tls_certfile = self._expandpath(tls_certfile)
        self.tls_keyfile = self._expandpath(tls_keyfile)
        self.tls_version = self._get_tls_version(tls_version)
        self.tls_ciphers = self._expandpath(tls_ciphers)
        self.tls_insecure = tls_insecure
        self.username = username
        self.password = password
        self.topics = set(topics or [])
        self.timeout = timeout
        self.on_connect = self.connect_hndl()
        self.on_disconnect = self.disconnect_hndl()

        if on_message:
            self.on_message = on_message  # type: ignore

        if username and password:
            self.username_pw_set(username, password)

        if tls_cafile:
            self.tls_set(
                ca_certs=self.tls_cafile,
                certfile=self.tls_certfile,
                keyfile=self.tls_keyfile,
                tls_version=self.tls_version,
                ciphers=self.tls_ciphers,
            )

            self.tls_insecure_set(self.tls_insecure)

        self._running = False
        self._stop_scheduled = False

    @staticmethod
    def _expandpath(path: Optional[str] = None) -> Optional[str]:
        """
        Utility method to expand a path string.
        """
        return os.path.abspath(os.path.expanduser(path)) if path else None

    @staticmethod
    def _get_tls_version(version: Optional[Union[str, IntEnum]] = None):
        """
        A utility method that normalizes an SSL version string or enum to a
        standard ``_SSLMethod`` enum.
        """
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

        raise AssertionError(f'Unrecognized TLS version: {version}')

    def connect(
        self,
        *args,
        host: Optional[str] = None,
        port: Optional[int] = None,
        keepalive: Optional[int] = None,
        **kwargs,
    ):
        """
        Overrides the default connect method.
        """
        if not self.is_connected():
            self.logger.debug(
                'Connecting to MQTT broker %s:%d, client_id=%s...',
                self.host,
                self.port,
                self.client_id,
            )

            return super().connect(
                host=host or self.host,
                port=port or self.port,
                keepalive=keepalive or self.timeout,
                *args,
                **kwargs,
            )

        return None

    @property
    def configuration(self) -> Dict[str, Any]:
        """
        :return: The configuration of the client.
        """
        return {
            'host': self.host,
            'port': self.port,
            'topics': self.topics,
            'on_message': self.on_message,
            'username': self.username,
            'password': self.password,
            'client_id': self.client_id,
            'tls_cafile': self.tls_cafile,
            'tls_certfile': self.tls_certfile,
            'tls_keyfile': self.tls_keyfile,
            'tls_version': self.tls_version,
            'tls_ciphers': self.tls_ciphers,
            'tls_insecure': self.tls_insecure,
            'timeout': self.timeout,
        }

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
            if topic not in self.topics:
                self.logger.info('The topic %s is not subscribed', topic)
                continue

            super().unsubscribe(topic, **kwargs)
            self.topics.remove(topic)

    def connect_hndl(self):
        """
        When the client connects, subscribe to all the registered topics.
        """

        def handler(*_, **__):
            self.logger.debug(
                'Connected to MQTT broker %s:%d, client_id=%s',
                self.host,
                self.port,
                self.client_id,
            )
            self.subscribe()

        return handler

    def disconnect_hndl(self):
        """
        Notifies the client disconnection.
        """

        def handler(*_, **__):
            self.logger.debug(
                'Disconnected from MQTT broker %s:%d, client_id=%s',
                self.host,
                self.port,
                self.client_id,
            )

        return handler

    def run(self):
        """
        Connects to the MQTT server, subscribes to all the registered topics
        and listens for messages.
        """
        super().run()
        self.connect()
        self._running = True
        self.loop_forever()

    def stop(self):
        """
        The stop method schedules the stop and disconnects the client.
        """
        if not self.is_alive():
            return

        try:
            self.loop_stop()
        except Exception as e:
            self.logger.debug('Could not stop client loop: %s: %s', type(e).__name__, e)

        self._stop_scheduled = True
        self.disconnect()
        self._running = False


# vim:sw=4:ts=4:et:
