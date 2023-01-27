import contextlib
import json
from typing import Mapping

from platypush.backend.mqtt import MqttBackend
from platypush.bus import Bus
from platypush.context import get_bus, get_plugin
from platypush.message.event.zigbee.mqtt import (
    ZigbeeMqttOnlineEvent,
    ZigbeeMqttOfflineEvent,
    ZigbeeMqttDevicePropertySetEvent,
    ZigbeeMqttDevicePairingEvent,
    ZigbeeMqttDeviceConnectedEvent,
    ZigbeeMqttDeviceBannedEvent,
    ZigbeeMqttDeviceRemovedEvent,
    ZigbeeMqttDeviceRemovedFailedEvent,
    ZigbeeMqttDeviceWhitelistedEvent,
    ZigbeeMqttDeviceRenamedEvent,
    ZigbeeMqttDeviceBindEvent,
    ZigbeeMqttDeviceUnbindEvent,
    ZigbeeMqttGroupAddedEvent,
    ZigbeeMqttGroupAddedFailedEvent,
    ZigbeeMqttGroupRemovedEvent,
    ZigbeeMqttGroupRemovedFailedEvent,
    ZigbeeMqttGroupRemoveAllEvent,
    ZigbeeMqttGroupRemoveAllFailedEvent,
    ZigbeeMqttErrorEvent,
)
from platypush.plugins.zigbee.mqtt import ZigbeeMqttPlugin


class ZigbeeMqttListener(MqttBackend):
    """
    Listener for zigbee2mqtt events.
    """

    def __init__(self):
        plugin = self._plugin
        self.base_topic = plugin.base_topic  # type: ignore
        self._devices = {}
        self._devices_info = {}
        self._groups = {}
        self._last_state = None
        self.server_info = {
            'host': plugin.host,  # type: ignore
            'port': plugin.port or self._default_mqtt_port,  # type: ignore
            'tls_cafile': plugin.tls_cafile,  # type: ignore
            'tls_certfile': plugin.tls_certfile,  # type: ignore
            'tls_ciphers': plugin.tls_ciphers,  # type: ignore
            'tls_keyfile': plugin.tls_keyfile,  # type: ignore
            'tls_version': plugin.tls_version,  # type: ignore
            'username': plugin.username,  # type: ignore
            'password': plugin.password,  # type: ignore
        }

        listeners = [
            {
                **self.server_info,
                'topics': [
                    self.base_topic + '/' + topic
                    for topic in [
                        'bridge/state',
                        'bridge/log',
                        'bridge/logging',
                        'bridge/devices',
                        'bridge/groups',
                    ]
                ],
            }
        ]

        super().__init__(
            subscribe_default_topic=False, listeners=listeners, **self.server_info
        )

        assert self.client_id
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

        self._bus.post(evt(host=client._host, port=client._port))
        self._last_state = msg

    def _process_log_message(self, client, msg):
        msg_type = msg.get('type')
        text = msg.get('message')
        args = {'host': client._host, 'port': client._port}

        if msg_type == 'devices':
            devices = {}
            for dev in text or []:
                devices[dev['friendly_name']] = dev
                client.subscribe(self.base_topic + '/' + dev['friendly_name'])
        elif msg_type == 'pairing':
            self._bus.post(ZigbeeMqttDevicePairingEvent(device=text, **args))
        elif msg_type in ['device_ban', 'device_banned']:
            self._bus.post(ZigbeeMqttDeviceBannedEvent(device=text, **args))
        elif msg_type in ['device_removed_failed', 'device_force_removed_failed']:
            force = msg_type == 'device_force_removed_failed'
            self._bus.post(
                ZigbeeMqttDeviceRemovedFailedEvent(device=text, force=force, **args)
            )
        elif msg_type == 'device_whitelisted':
            self._bus.post(ZigbeeMqttDeviceWhitelistedEvent(device=text, **args))
        elif msg_type == 'device_renamed':
            self._bus.post(ZigbeeMqttDeviceRenamedEvent(device=text, **args))
        elif msg_type == 'device_bind':
            self._bus.post(ZigbeeMqttDeviceBindEvent(device=text, **args))
        elif msg_type == 'device_unbind':
            self._bus.post(ZigbeeMqttDeviceUnbindEvent(device=text, **args))
        elif msg_type == 'device_group_add':
            self._bus.post(ZigbeeMqttGroupAddedEvent(group=text, **args))
        elif msg_type == 'device_group_add_failed':
            self._bus.post(ZigbeeMqttGroupAddedFailedEvent(group=text, **args))
        elif msg_type == 'device_group_remove':
            self._bus.post(ZigbeeMqttGroupRemovedEvent(group=text, **args))
        elif msg_type == 'device_group_remove_failed':
            self._bus.post(ZigbeeMqttGroupRemovedFailedEvent(group=text, **args))
        elif msg_type == 'device_group_remove_all':
            self._bus.post(ZigbeeMqttGroupRemoveAllEvent(group=text, **args))
        elif msg_type == 'device_group_remove_all_failed':
            self._bus.post(ZigbeeMqttGroupRemoveAllFailedEvent(group=text, **args))
        elif msg_type == 'zigbee_publish_error':
            self.logger.error('zigbee2mqtt error: {}'.format(text))
            self._bus.post(ZigbeeMqttErrorEvent(error=text, **args))
        elif msg.get('level') in ['warning', 'error']:
            log = getattr(self.logger, msg['level'])
            log(
                'zigbee2mqtt {}: {}'.format(
                    msg['level'], text or msg.get('error', msg.get('warning'))
                )
            )

    def _process_devices(self, client, msg):
        devices_info = {
            device.get('friendly_name', device.get('ieee_address')): device
            for device in msg
        }

        # noinspection PyProtectedMember
        event_args = {'host': client._host, 'port': client._port}
        client.subscribe(
            *[self.base_topic + '/' + device for device in devices_info.keys()]
        )

        for name, device in devices_info.items():
            if name not in self._devices:
                self._bus.post(
                    ZigbeeMqttDeviceConnectedEvent(device=name, **event_args)
                )

            exposes = (device.get('definition', {}) or {}).get('exposes', [])
            payload = self._plugin._build_device_get_request(exposes)  # type: ignore
            if payload:
                client.publish(
                    self.base_topic + '/' + name + '/get',
                    json.dumps(payload),
                )

        devices_copy = [*self._devices.keys()]
        for name in devices_copy:
            if name not in devices_info:
                self._bus.post(ZigbeeMqttDeviceRemovedEvent(device=name, **event_args))
                del self._devices[name]

        self._devices = {device: {} for device in devices_info.keys()}
        self._devices_info = devices_info

    def _process_groups(self, client, msg):
        # noinspection PyProtectedMember
        event_args = {'host': client._host, 'port': client._port}
        groups_info = {
            group.get('friendly_name', group.get('id')): group for group in msg
        }

        for name in groups_info.keys():
            if name not in self._groups:
                self._bus.post(ZigbeeMqttGroupAddedEvent(group=name, **event_args))

        groups_copy = [*self._groups.keys()]
        for name in groups_copy:
            if name not in groups_info:
                self._bus.post(ZigbeeMqttGroupRemovedEvent(group=name, **event_args))
                del self._groups[name]

        self._groups = {group: {} for group in groups_info.keys()}

    def on_mqtt_message(self):
        def handler(client, _, msg):
            topic = msg.topic[len(self.base_topic) + 1 :]
            data = msg.payload.decode()
            if not data:
                return

            with contextlib.suppress(ValueError, TypeError):
                data = json.loads(data)

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
                changed_props = {
                    k: v for k, v in data.items() if v != self._devices[name].get(k)
                }

                if changed_props:
                    self._process_property_update(name, data)
                    self._bus.post(
                        ZigbeeMqttDevicePropertySetEvent(
                            host=client._host,
                            port=client._port,
                            device=name,
                            properties=changed_props,
                        )
                    )

                self._devices[name].update(data)

        return handler

    @property
    def _plugin(self) -> ZigbeeMqttPlugin:
        plugin = get_plugin('zigbee.mqtt')
        assert plugin, 'The zigbee.mqtt plugin is not configured'
        return plugin

    @property
    def _bus(self) -> Bus:
        return get_bus()

    def _process_property_update(self, device_name: str, properties: Mapping):
        device_info = self._devices_info.get(device_name)
        if not (device_info and properties):
            return

        self._plugin.publish_entities(  # type: ignore
            [
                {
                    **device_info,
                    'state': properties,
                }
            ]
        )

    def run(self):
        super().run()


# vim:sw=4:ts=4:et:
