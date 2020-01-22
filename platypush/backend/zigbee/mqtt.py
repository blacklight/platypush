import json
from typing import Optional

from platypush.backend.mqtt import MqttBackend
from platypush.context import get_plugin
from platypush.message.event.zigbee.mqtt import ZigbeeMqttOnlineEvent, ZigbeeMqttOfflineEvent, \
        ZigbeeMqttDevicePropertySetEvent, ZigbeeMqttDevicePairingEvent, ZigbeeMqttDeviceConnectedEvent, \
        ZigbeeMqttDeviceBannedEvent, ZigbeeMqttDeviceRemovedEvent, ZigbeeMqttDeviceRemovedFailedEvent, \
        ZigbeeMqttDeviceWhitelistedEvent, ZigbeeMqttDeviceRenamedEvent, ZigbeeMqttDeviceBindEvent, \
        ZigbeeMqttDeviceUnbindEvent, ZigbeeMqttGroupAddedEvent, ZigbeeMqttGroupAddedFailedEvent, \
        ZigbeeMqttGroupRemovedEvent, ZigbeeMqttGroupRemovedFailedEvent, ZigbeeMqttGroupRemoveAllEvent, \
        ZigbeeMqttGroupRemoveAllFailedEvent, ZigbeeMqttErrorEvent


class ZigbeeMqttBackend(MqttBackend):
    """
    Listen for events on a zigbee2mqtt service.

    Triggers:

        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttOnlineEvent` when the service comes online.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttOfflineEvent` when the service goes offline.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePropertySetEvent` when the properties of a
          connected device change.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePairingEvent` when a device is pairing.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceConnectedEvent` when a device connects
          to the network.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBannedEvent` when a device is banned
          from the network.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedEvent` when a device is removed
          from the network.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedFailedEvent` when a request to
          remove a device from the network fails.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceWhitelistedEvent` when a device is
          whitelisted on the network.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRenamedEvent` when a device is
          renamed on the network.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBindEvent` when a device bind event
          occurs.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceUnbindEvent` when a device unbind event
          occurs.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedEvent` when a group is added.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedFailedEvent` when a request to
          add a new group fails.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedEvent` when a group is removed.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedFailedEvent` when a request to
          remove a group fails.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllEvent` when all the devices
          are removed from a group.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllFailedEvent` when a request to
          remove all the devices from a group fails.
        * :class:`platypush.message.event.zigbee.mqtt.ZigbeeMqttErrorEvent` when an internal error occurs
          on the zigbee2mqtt service.

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)
        * The :class:`platypush.plugins.zigbee.mqtt.ZigbeeMqttPlugin` plugin configured.

    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, base_topic='zigbee2mqtt',
                 tls_cafile: Optional[str] = None, tls_certfile: Optional[str] = None,
                 tls_keyfile: Optional[str] = None, tls_version: Optional[str] = None,
                 tls_ciphers: Optional[str] = None, username: Optional[str] = None,
                 password: Optional[str] = None, *args, **kwargs):
        """
        :param host: MQTT broker host (default: host configured on the ``zigbee.mqtt`` plugin).
        :param port: MQTT broker port (default: 1883).
        :param base_topic: Prefix of the topics published by zigbee2mqtt (default: '``zigbee2mqtt``').
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
        """

        if host:
            self.base_topic = base_topic
            listeners = [{
                'host': host,
                'port': port or self._default_mqtt_port,
                'tls_cafile': tls_cafile,
                'tls_certfile': tls_certfile,
                'tls_ciphers': tls_ciphers,
                'tls_keyfile': tls_keyfile,
                'tls_version': tls_version,
                'username': username,
                'password': password,
                'topics': [
                    base_topic + '/' + topic
                    for topic in ['bridge/state', 'bridge/log']
                ],
            }]
        else:
            plugin = get_plugin('zigbee.mqtt')
            self.base_topic = plugin.base_topic
            listeners = [{
                'host': plugin.host,
                'port': plugin.port or self._default_mqtt_port,
                'tls_cafile': plugin.tls_cafile,
                'tls_certfile': plugin.tls_certfile,
                'tls_ciphers': plugin.tls_ciphers,
                'username': plugin.username,
                'password': plugin.password,
                'topics': [
                    plugin.base_topic + '/' + topic
                    for topic in ['bridge/state', 'bridge/log']
                ],
            }]

        super().__init__(subscribe_default_topic=False, listeners=listeners, *args, **kwargs)
        self._devices = {}

    def _process_state_message(self, client, msg):
        if msg == 'online':
            evt = ZigbeeMqttOnlineEvent
            self._refresh_devices(client)
        elif msg == 'offline':
            evt = ZigbeeMqttOfflineEvent
            self.logger.warning('zigbee2mqtt service is offline')
        else:
            return

        # noinspection PyProtectedMember
        self.bus.post(evt(host=client._host, port=client._port))

    def _refresh_devices(self, client):
        client.publish(self.base_topic + '/' + 'bridge/config/devices/get')

    def _process_log_message(self, client, msg):
        msg_type = msg.get('type')
        msg = msg.get('message')
        # noinspection PyProtectedMember
        args = {'host': client._host, 'port': client._port}

        if msg_type == 'devices':
            devices = {}
            for dev in (msg or []):
                devices[dev['friendly_name']] = dev
                client.subscribe(self.base_topic + '/' + dev['friendly_name'])

            self._devices = devices
        elif msg_type == 'pairing':
            self.bus.post(ZigbeeMqttDevicePairingEvent(device=msg, **args))
        elif msg_type == 'device_connected':
            self.bus.post(ZigbeeMqttDeviceConnectedEvent(device=msg, **args))
            self._refresh_devices(client)
        elif msg_type in ['device_ban', 'device_banned']:
            self.bus.post(ZigbeeMqttDeviceBannedEvent(device=msg, **args))
        elif msg_type in ['device_removed', 'device_force_removed']:
            force = msg_type == 'device_force_removed'
            self.bus.post(ZigbeeMqttDeviceRemovedEvent(device=msg, force=force, **args))
        elif msg_type in ['device_removed_failed', 'device_force_removed_failed']:
            force = msg_type == 'device_force_removed_failed'
            self.bus.post(ZigbeeMqttDeviceRemovedFailedEvent(device=msg, force=force, **args))
        elif msg_type == 'device_whitelisted':
            self.bus.post(ZigbeeMqttDeviceWhitelistedEvent(device=msg, **args))
        elif msg_type == 'device_renamed':
            self.bus.post(ZigbeeMqttDeviceRenamedEvent(device=msg, **args))
            self._refresh_devices(client)
        elif msg_type == 'device_bind':
            self.bus.post(ZigbeeMqttDeviceBindEvent(device=msg, **args))
        elif msg_type == 'device_unbind':
            self.bus.post(ZigbeeMqttDeviceUnbindEvent(device=msg, **args))
        elif msg_type == 'device_group_add':
            self.bus.post(ZigbeeMqttGroupAddedEvent(group=msg, **args))
        elif msg_type == 'device_group_add_failed':
            self.bus.post(ZigbeeMqttGroupAddedFailedEvent(group=msg, **args))
        elif msg_type == 'device_group_remove':
            self.bus.post(ZigbeeMqttGroupRemovedEvent(group=msg, **args))
        elif msg_type == 'device_group_remove_failed':
            self.bus.post(ZigbeeMqttGroupRemovedFailedEvent(group=msg, **args))
        elif msg_type == 'device_group_remove_all':
            self.bus.post(ZigbeeMqttGroupRemoveAllEvent(group=msg, **args))
        elif msg_type == 'device_group_remove_all_failed':
            self.bus.post(ZigbeeMqttGroupRemoveAllFailedEvent(group=msg, **args))
        elif msg_type == 'zigbee_publish_error':
            self.logger.warning('zigbee2mqtt internal error: {}'.format(msg))
            self.bus.post(ZigbeeMqttErrorEvent(error=msg, **args))

    def on_mqtt_message(self):
        def handler(client, _, msg):
            topic = msg.topic[len(self.base_topic)+1:]
            data = msg.payload.decode()

            # noinspection PyBroadException
            try:
                data = json.loads(data)
            except:
                pass

            if topic == 'bridge/state':
                self._process_state_message(client, data)
            elif topic == 'bridge/log':
                self._process_log_message(client, data)
            else:
                # noinspection PyProtectedMember
                self.bus.post(ZigbeeMqttDevicePropertySetEvent(host=client._host, port=client._port,
                                                               device=topic, properties=data))

        return handler


# vim:sw=4:ts=4:et:
