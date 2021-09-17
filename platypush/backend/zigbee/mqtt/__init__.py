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
                 password: Optional[str] = None, client_id: Optional[str] = None, *args, **kwargs):
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
        :param client_id: MQTT client ID (default: ``<device_id>-zigbee-mqtt``, to prevent clashes with the
            :class:`platypush.backend.mqtt.MqttBackend` ``client_id``.
        """

        plugin = get_plugin('zigbee.mqtt')
        self.base_topic = base_topic or plugin.base_topic
        self._devices = {}
        self._groups = {}
        self._last_state = None
        self.server_info = {
            'host': host or plugin.host,
            'port': port or plugin.port or self._default_mqtt_port,
            'tls_cafile': tls_cafile or plugin.tls_cafile,
            'tls_certfile': tls_certfile or plugin.tls_certfile,
            'tls_ciphers': tls_ciphers or plugin.tls_ciphers,
            'tls_keyfile': tls_keyfile or plugin.tls_keyfile,
            'tls_version': tls_version or plugin.tls_version,
            'username': username or plugin.username,
            'password': password or plugin.password,
        }

        kwargs = {
            **kwargs,
            **self.server_info,
        }

        listeners = [{
            **self.server_info,
            'topics': [
                self.base_topic + '/' + topic
                for topic in ['bridge/state', 'bridge/log', 'bridge/logging', 'bridge/devices', 'bridge/groups']
            ],
        }]

        super().__init__(
            *args, subscribe_default_topic=False,
            listeners=listeners, client_id=client_id, **kwargs
        )

        if not client_id:
            self.client_id += '-zigbee-mqtt'

    def _process_state_message(self, client, msg):
        if msg == self._last_state:
            return

        if msg == 'online':
            evt = ZigbeeMqttOnlineEvent
        elif msg == 'offline':
            evt = ZigbeeMqttOfflineEvent
            self.logger.warning('zigbee2mqtt service is offline')
        else:
            return

        # noinspection PyProtectedMember
        self.bus.post(evt(host=client._host, port=client._port))
        self._last_state = msg

    def _process_log_message(self, client, msg):
        msg_type = msg.get('type')
        text = msg.get('message')
        # noinspection PyProtectedMember
        args = {'host': client._host, 'port': client._port}

        if msg_type == 'devices':
            devices = {}
            for dev in (text or []):
                devices[dev['friendly_name']] = dev
                client.subscribe(self.base_topic + '/' + dev['friendly_name'])
        elif msg_type == 'pairing':
            self.bus.post(ZigbeeMqttDevicePairingEvent(device=text, **args))
        elif msg_type in ['device_ban', 'device_banned']:
            self.bus.post(ZigbeeMqttDeviceBannedEvent(device=text, **args))
        elif msg_type in ['device_removed_failed', 'device_force_removed_failed']:
            force = msg_type == 'device_force_removed_failed'
            self.bus.post(ZigbeeMqttDeviceRemovedFailedEvent(device=text, force=force, **args))
        elif msg_type == 'device_whitelisted':
            self.bus.post(ZigbeeMqttDeviceWhitelistedEvent(device=text, **args))
        elif msg_type == 'device_renamed':
            self.bus.post(ZigbeeMqttDeviceRenamedEvent(device=text, **args))
        elif msg_type == 'device_bind':
            self.bus.post(ZigbeeMqttDeviceBindEvent(device=text, **args))
        elif msg_type == 'device_unbind':
            self.bus.post(ZigbeeMqttDeviceUnbindEvent(device=text, **args))
        elif msg_type == 'device_group_add':
            self.bus.post(ZigbeeMqttGroupAddedEvent(group=text, **args))
        elif msg_type == 'device_group_add_failed':
            self.bus.post(ZigbeeMqttGroupAddedFailedEvent(group=text, **args))
        elif msg_type == 'device_group_remove':
            self.bus.post(ZigbeeMqttGroupRemovedEvent(group=text, **args))
        elif msg_type == 'device_group_remove_failed':
            self.bus.post(ZigbeeMqttGroupRemovedFailedEvent(group=text, **args))
        elif msg_type == 'device_group_remove_all':
            self.bus.post(ZigbeeMqttGroupRemoveAllEvent(group=text, **args))
        elif msg_type == 'device_group_remove_all_failed':
            self.bus.post(ZigbeeMqttGroupRemoveAllFailedEvent(group=text, **args))
        elif msg_type == 'zigbee_publish_error':
            self.logger.error('zigbee2mqtt error: {}'.format(text))
            self.bus.post(ZigbeeMqttErrorEvent(error=text, **args))
        elif msg.get('level') in ['warning', 'error']:
            log = getattr(self.logger, msg['level'])
            log('zigbee2mqtt {}: {}'.format(msg['level'], text or msg.get('error', msg.get('warning'))))

    def _process_devices(self, client, msg):
        devices_info = {
            device.get('friendly_name', device.get('ieee_address')): device
            for device in msg
        }

        # noinspection PyProtectedMember
        event_args = {'host': client._host, 'port': client._port}
        client.subscribe(*[
            self.base_topic + '/' + device
            for device in devices_info.keys()
        ])

        for name, device in devices_info.items():
            if name not in self._devices:
                self.bus.post(ZigbeeMqttDeviceConnectedEvent(device=name, **event_args))

            exposes = (device.get('definition', {}) or {}).get('exposes', [])
            client.publish(
                self.base_topic + '/' + name + '/get',
                json.dumps(get_plugin('zigbee.mqtt').build_device_get_request(exposes))
            )

        devices_copy = [*self._devices.keys()]
        for name in devices_copy:
            if name not in devices_info:
                self.bus.post(ZigbeeMqttDeviceRemovedEvent(device=name, **event_args))
                del self._devices[name]

        self._devices = {device: {} for device in devices_info.keys()}

    def _process_groups(self, client, msg):
        # noinspection PyProtectedMember
        event_args = {'host': client._host, 'port': client._port}
        groups_info = {
            group.get('friendly_name', group.get('id')): group
            for group in msg
        }

        for name in groups_info.keys():
            if name not in self._groups:
                self.bus.post(ZigbeeMqttGroupAddedEvent(group=name, **event_args))

        groups_copy = [*self._groups.keys()]
        for name in groups_copy:
            if name not in groups_info:
                self.bus.post(ZigbeeMqttGroupRemovedEvent(group=name, **event_args))
                del self._groups[name]

        self._groups = {group: {} for group in groups_info.keys()}

    def on_mqtt_message(self):
        def handler(client, _, msg):
            topic = msg.topic[len(self.base_topic)+1:]
            data = msg.payload.decode()
            if not data:
                return

            try:
                data = json.loads(data)
            except (ValueError, TypeError):
                pass

            if topic == 'bridge/state':
                self._process_state_message(client, data)
            elif topic in ['bridge/log', 'bridge/logging']:
                self._process_log_message(client, data)
            elif topic == 'bridge/devices':
                self._process_devices(client, data)
            elif topic == 'bridge/groups':
                self._process_groups(client, data)
            else:
                suffix = topic.split('/')[-1]
                if suffix not in self._devices:
                    return

                name = suffix
                changed_props = {k: v for k, v in data.items() if v != self._devices[name].get(k)}

                if changed_props:
                    # noinspection PyProtectedMember
                    self.bus.post(ZigbeeMqttDevicePropertySetEvent(host=client._host, port=client._port,
                                                                   device=name, properties=changed_props))

                self._devices[name].update(data)

        return handler

    def run(self):
        super().run()


# vim:sw=4:ts=4:et:
