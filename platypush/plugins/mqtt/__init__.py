from collections import defaultdict
import hashlib
import io
import json
import threading
from typing import Any, Dict, Iterable, Optional, IO

import paho.mqtt.client as mqtt

from platypush.config import Config
from platypush.context import get_bus
from platypush.message import Message
from platypush.message.event.mqtt import MQTTMessageEvent
from platypush.message.request import Request
from platypush.plugins import RunnablePlugin, action
from platypush.utils import get_message_response

from ._client import DEFAULT_TIMEOUT, MqttCallback, MqttClient


class MqttPlugin(RunnablePlugin):
    """
    This plugin allows you to send custom message to a message queue compatible
    with the MQTT protocol, see https://mqtt.org/
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 1883,
        topics: Optional[Iterable[str]] = None,
        tls_cafile: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version: Optional[str] = None,
        tls_ciphers: Optional[str] = None,
        tls_insecure: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        run_topic_prefix: Optional[str] = None,
        listeners: Optional[Iterable[dict]] = None,
        **kwargs,
    ):
        """
        :param host: If set, MQTT messages will by default routed to this host
            unless overridden in `send_message` (default: None)
        :param port: If a default host is set, specify the listen port
            (default: 1883)
        :param topics: If a default ``host`` is specified, then this list will
            include a default list of topics that should be subscribed on that
            broker at startup.
        :param tls_cafile: If a default host is set and requires TLS/SSL,
            specify the certificate authority file (default: None)
        :param tls_certfile: If a default host is set and requires TLS/SSL,
            specify the certificate file (default: None)
        :param tls_keyfile: If a default host is set and requires TLS/SSL,
            specify the key file (default: None)
        :param tls_version: If TLS/SSL is enabled on the MQTT server and it
            requires a certain TLS version, specify it here (default: None).
            Supported versions: ``tls`` (automatic), ``tlsv1``, ``tlsv1.1``,
            ``tlsv1.2``.
        :param tls_ciphers: If a default host is set and requires TLS/SSL,
            specify the supported ciphers (default: None)
        :param tls_insecure: Set to True to ignore TLS insecure warnings
            (default: False).
        :param username: If a default host is set and requires user
            authentication, specify the username ciphers (default: None)
        :param password: If a default host is set and requires user
            authentication, specify the password ciphers (default: None)
        :param client_id: ID used to identify the client on the MQTT server
            (default: None). If None is specified then
            ``Config.get('device_id')`` will be used.
        :param timeout: Client timeout in seconds (default: 30 seconds).
        :param run_topic_prefix: If specified, the MQTT plugin will listen for
            messages on a topic in the format `{run_topic_prefix}/{device_id}.
            When a message is received, it will interpret it as a JSON request
            to execute, in the format
            ``{"type": "request", "action": "plugin.action", "args": {...}}``.

            .. warning:: This parameter is mostly kept for backwards
                compatibility, but you should avoid it - unless the MQTT broker
                is on a personal safe network that you own, or it requires
                user authentication and it uses SSL. The reason is that the
                messages received on this topic won't be subject to token
                verification, allowing unauthenticated arbitrary command
                execution on the target host. If you still want the ability of
                running commands remotely over an MQTT broker, then you may
                consider creating a dedicated topic listener with an attached
                event hook on
                :class:`platypush.message.event.mqtt.MQTTMessageEvent`. The
                hook can implement whichever authentication logic you like.

        :param listeners: If specified, the MQTT plugin will listen for
            messages on these topics. Use this parameter if you also want to
            listen on other MQTT brokers other than the primary one. This
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
                          port: 11883
                          username: myuser
                          password: secret
                          topics:
                              - topic4
                              - topic5

        """
        super().__init__(**kwargs)

        self.client_id = client_id or str(Config.get('device_id'))
        self.run_topic = (
            f'{run_topic_prefix}/{Config.get("device_id")}'
            if type(self) == MqttPlugin and run_topic_prefix
            else None
        )

        self._listeners_lock = defaultdict(threading.RLock)
        self.listeners: Dict[str, MqttClient] = {}  # client_id -> MqttClient map
        self.timeout = timeout
        self.default_listener = (
            self._get_client(
                host=host,
                port=port,
                topics=(
                    (tuple(topics) if topics else ())
                    + ((self.run_topic,) if self.run_topic else ())
                ),
                on_message=self.on_mqtt_message(),
                tls_cafile=tls_cafile,
                tls_certfile=tls_certfile,
                tls_keyfile=tls_keyfile,
                tls_version=tls_version,
                tls_ciphers=tls_ciphers,
                tls_insecure=tls_insecure,
                username=username,
                password=password,
                client_id=client_id,
                timeout=timeout,
            )
            if host
            else None
        )

        for listener in listeners or []:
            self._get_client(
                **self._mqtt_args(on_message=self.on_mqtt_message(), **listener)
            )

    def _get_client_id(
        self,
        host: str,
        port: int,
        client_id: Optional[str] = None,
        topics: Iterable[str] = (),
        **_,
    ) -> str:
        """
        Calculates a unique client ID given an MQTT configuration.
        """
        client_id = client_id or self.client_id
        client_hash = hashlib.sha1(
            '|'.join(
                [
                    self.__class__.__name__,
                    host,
                    str(port),
                    json.dumps(sorted(topics)),
                ]
            ).encode()
        ).hexdigest()

        return f'{client_id}-{client_hash}'

    def _mqtt_args(
        self,
        host: Optional[str] = None,
        port: int = 1883,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        topics: Iterable[str] = (),
        **kwargs,
    ):
        """
        :return: An MQTT configuration mapping that uses either the specified
            arguments (if host is specified), or falls back to the default
            configurated arguments.
        """
        default_conf = (
            self.default_listener.configuration if self.default_listener else {}
        )

        if not host:
            assert (
                self.default_listener
            ), 'No host specified and no configured default host'

            return {
                **default_conf,
                'topics': (*self.default_listener.topics, *topics),
            }

        return {
            'host': host,
            'port': port,
            'timeout': timeout or default_conf.get('timeout'),
            'topics': topics,
            **kwargs,
        }

    def on_mqtt_message(self) -> MqttCallback:
        """
        Default MQTT message handler. It forwards a
        :class:`platypush.message.event.mqtt.MQTTMessageEvent` event to the
        bus.
        """

        def handler(client: MqttClient, _, msg: mqtt.MQTTMessage):
            data = msg.payload
            try:
                data = data.decode('utf-8')
                data = json.loads(data)
            except (TypeError, AttributeError, ValueError):
                # Not a serialized JSON
                pass

            if self.default_listener and msg.topic == self.run_topic:
                try:
                    app_msg = Message.build(data)
                    self.on_exec_message(client, app_msg)
                except Exception as e:
                    self.logger.warning(
                        'Message execution error: %s: %s', type(e).__name__, str(e)
                    )
            else:
                get_bus().post(
                    MQTTMessageEvent(
                        host=client.host, port=client.port, topic=msg.topic, msg=data
                    )
                )

        return handler

    def on_exec_message(self, client: MqttClient, msg):
        """
        Message handler for (legacy) application requests over MQTT.
        """

        def response_thread(req: Request):
            """
            A separate thread to handle the response to a request.
            """
            if not self.run_topic:
                return

            response = get_message_response(req)
            if not response:
                return

            response_topic = f'{self.run_topic}/responses/{req.id}'
            self.logger.info(
                'Processing response on the MQTT topic %s: %s',
                response_topic,
                response,
            )

            client.publish(payload=str(response), topic=response_topic)

        self.logger.info('Received message on the MQTT backend: %s', msg)

        try:
            get_bus().post(msg)
        except Exception as e:
            self.logger.exception(e)
            return

        if isinstance(msg, Request):
            threading.Thread(
                target=response_thread,
                name='MQTTProcessorResponseThread',
                args=(msg,),
            ).start()

    def _get_client(
        self,
        host: Optional[str] = None,
        port: int = 1883,
        topics: Iterable[str] = (),
        client_id: Optional[str] = None,
        on_message: Optional[MqttCallback] = None,
        **kwargs,
    ) -> MqttClient:
        """
        :return: A :class:`platypush.message.event.mqtt.MqttClient` instance.
          It will return the existing client with the given inferred ID if it
          already exists, or it will register a new one.
        """
        if host:
            kwargs['host'] = host
            kwargs['port'] = port
        else:
            assert (
                self.default_listener
            ), 'No host specified and no configured default host'
            kwargs = self.default_listener.configuration

        on_message = on_message or self.on_mqtt_message()
        kwargs.update(
            {
                'topics': topics,
                'on_message': on_message,
                'client_id': client_id,
            }
        )

        client_id = self._get_client_id(
            host=kwargs['host'],
            port=kwargs['port'],
            client_id=client_id,
            topics=topics,
        )

        kwargs['client_id'] = client_id
        with self._listeners_lock[client_id]:
            client = self.listeners.get(client_id)
            if not (client and client.is_alive()):
                client = self.listeners[
                    client_id
                ] = MqttClient(  # pylint: disable=E1125
                    **kwargs
                )

        if topics:
            client.subscribe(*topics)

        return client

    @action
    def publish(
        self,
        topic: str,
        msg: Any,
        qos: int = 0,
        reply_topic: Optional[str] = None,
        **mqtt_kwargs,
    ):
        """
        Sends a message to a topic.

        :param topic: Topic/channel where the message will be delivered
        :param msg: Message to be sent. It can be a list, a dict, or a Message
            object.
        :param qos: Quality of Service (_QoS_) for the message - see `MQTT QoS
            <https://assetwolf.com/learn/mqtt-qos-understanding-quality-of-service>`_
            (default: 0).
        :param reply_topic: If a ``reply_topic`` is specified, then the action
            will wait for a response on this topic.
        :param mqtt_kwargs: MQTT broker configuration (host, port, username,
            password etc.). See :meth:`.__init__` parameters.
        """
        response_buffer = io.BytesIO()
        client = None

        try:
            # Try to parse it as a Platypush message or dump it to JSON from a dict/list
            if isinstance(msg, (dict, list)):
                msg = json.dumps(msg)

                try:
                    msg = Message.build(json.loads(msg))
                except (KeyError, TypeError, ValueError):
                    pass

            client = self._get_client(**mqtt_kwargs)
            client.connect()
            response_received = threading.Event()

            # If it's a request, then wait for the response
            if (
                isinstance(msg, Request)
                and self.default_listener
                and client.host == self.default_listener.host
                and self.run_topic
                and topic == self.run_topic
            ):
                reply_topic = f'{self.run_topic}/responses/{msg.id}'

            if reply_topic:
                client.on_message = self._response_callback(
                    reply_topic=reply_topic,
                    event=response_received,
                    buffer=response_buffer,
                )
                client.subscribe(reply_topic)

            client.publish(topic, str(msg), qos=qos)
            if not reply_topic:
                return None

            client.loop_start()
            ok = response_received.wait(timeout=client.timeout)
            if not ok:
                raise TimeoutError('Response timed out')

            return response_buffer.getvalue()
        finally:
            response_buffer.close()

            if client:
                client.stop()
                del client

    @action
    def subscribe(self, topic: str, **mqtt_kwargs):
        """
        Programmatically subscribe to a topic on an MQTT broker.

        Messages received on this topic will trigger a
        :class:`platypush.message.event.mqtt.MQTTMessageEvent` event that you
        can subscribe to.

        :param topic: Topic to subscribe to.
        :param mqtt_kwargs: MQTT broker configuration (host, port, username,
            password etc.). See :meth:`.__init__` parameters.
        """
        client = self._get_client(
            topics=(topic,), on_message=self.on_mqtt_message(), **mqtt_kwargs
        )

        if not client.is_alive():
            client.start()

    @action
    def unsubscribe(self, topic: str, **mqtt_kwargs):
        """
        Programmatically unsubscribe from a topic on an MQTT broker.

        :param topic: Topic to unsubscribe from.
        :param mqtt_kwargs: MQTT broker configuration (host, port, username,
            password etc.). See :meth:`.__init__` parameters.
        """
        client_id = self._get_client_id(
            topics=(topic,),
            **mqtt_kwargs,
        )

        with self._listeners_lock[client_id]:
            client = self.listeners.get(client_id)

        if not client:
            self.logger.info('No subscriptions found for topic %s', topic)
            return

        client.unsubscribe(topic)
        client.stop()
        del client

    def _response_callback(
        self, reply_topic: str, event: threading.Event, buffer: IO[bytes]
    ):
        """
        A response callback that writes the response to an IOBuffer and stops
        the client loop.
        """

        def on_message(client, _, msg):
            if msg.topic != reply_topic:
                return

            try:
                buffer.write(msg.payload)
                client.loop_stop()
            except Exception as e:
                self.logger.warning(
                    'Could not write the response back to the MQTT client: %s', e
                )
            finally:
                event.set()

        return on_message

    @action
    def send_message(self, *args, **kwargs):
        """
        Legacy alias for :meth:`platypush.plugins.mqtt.MqttPlugin.publish`.
        """
        return self.publish(*args, **kwargs)

    def main(self):
        if self.run_topic:
            self.logger.warning(
                'The MQTT integration is listening for commands on the topic %s.\n'
                'This approach is unsafe, as it allows any client to run unauthenticated requests.\n'
                'Please only enable it in test/trusted environments.',
                self.run_topic,
            )

        for listener in self.listeners.values():
            listener.start()

        self.wait_stop()

    def stop(self):
        """
        Disconnect all the clients upon plugin stop.
        """
        for listener in self.listeners.values():
            listener.stop()

        super().stop()

        for listener in self.listeners.values():
            try:
                listener.join(timeout=1)
                del listener
            except Exception:
                pass


# vim:sw=4:ts=4:et:
