import contextlib
import json
from queue import Queue, Empty
from typing import Optional, Type

from platypush.backend.mqtt import MqttBackend
from platypush.context import get_bus, get_plugin

from platypush.config import Config
from platypush.message.event.zwave import (
    ZwaveEvent,
    ZwaveNodeAddedEvent,
    ZwaveValueChangedEvent,
    ZwaveNodeRemovedEvent,
    ZwaveNodeRenamedEvent,
    ZwaveNodeReadyEvent,
    ZwaveNodeEvent,
    ZwaveNodeAsleepEvent,
    ZwaveNodeAwakeEvent,
    ZwaveValueRemovedEvent,
)


class ZwaveMqttListener(MqttBackend):
    """
    Internal MQTT listener for ``zwave.mqtt`` events.
    """

    def __init__(self, *args, **kwargs):
        self._nodes = {}
        self._groups = {}
        self._last_state = None
        self._events_queue = Queue()
        self.events_topic = self.plugin.events_topic
        self.server_info = {
            'host': self.plugin.host,
            'port': self.plugin.port or self._default_mqtt_port,
            'tls_cafile': self.plugin.tls_cafile,
            'tls_certfile': self.plugin.tls_certfile,
            'tls_ciphers': self.plugin.tls_ciphers,
            'tls_keyfile': self.plugin.tls_keyfile,
            'tls_version': self.plugin.tls_version,
            'username': self.plugin.username,
            'password': self.plugin.password,
        }

        listeners = [
            {
                **self.server_info,
                'topics': [
                    self.plugin.events_topic + '/node/' + topic
                    for topic in [
                        'node_ready',
                        'node_sleep',
                        'node_value_updated',
                        'node_metadata_updated',
                        'node_wakeup',
                    ]
                ],
            }
        ]

        super().__init__(
            *args,
            subscribe_default_topic=False,
            listeners=listeners,
            **kwargs,
        )

        self.client_id = (
            str(self.client_id or Config.get('device_id')) + '-zwavejs-mqtt'
        )

    @property
    def plugin(self):
        from platypush.plugins.zwave.mqtt import ZwaveMqttPlugin

        plugin: Optional[ZwaveMqttPlugin] = get_plugin('zwave.mqtt')
        assert plugin, 'The zwave.mqtt plugin is not configured'
        return plugin

    def _dispatch_event(
        self,
        event_type: Type[ZwaveEvent],
        node: dict,
        value: Optional[dict] = None,
        **kwargs,
    ):
        node_id = node.get('id')
        assert node_id is not None, 'No node ID specified'

        # This is far from efficient (we are querying the latest version of the whole
        # node for every event we receive), but this is the best we can do with recent
        # versions of ZWaveJS that only transmit partial representations of the node and
        # the value. The alternative would be to come up with a complex logic for merging
        # cached and new values, with the risk of breaking back-compatibility with earlier
        # implementations of zwavejs2mqtt.
        node = kwargs['node'] = self.plugin.get_nodes(node_id).output  # type: ignore
        node_values = node.get('values', {})

        if node and value:
            # Infer the value_id structure if it's not provided on the event
            value_id = value.get('id')
            if value_id is None:
                value_id = f"{value['commandClass']}-{value.get('endpoint', 0)}-{value['property']}"
                if 'propertyKey' in value:
                    value_id += '-' + str(value['propertyKey'])

                # Prepend the node_id to value_id if it's not available in node['values']
                # (compatibility with more recent versions of ZwaveJS that don't provide
                # the value_id on the events)
                if value_id not in node_values:
                    value_id = f"{node_id}-{value_id}"

            if value_id not in node_values:
                self.logger.warning(
                    'value_id %s not found on node %s', value_id, node_id
                )
                return

            value = kwargs['value'] = node_values[value_id]

        if issubclass(event_type, ZwaveNodeEvent):
            # If the node has been removed, remove it from the cache
            if event_type == ZwaveNodeRemovedEvent:
                self._nodes.pop(node_id, None)
            # If this node_id wasn't cached before, then it's a new node
            elif node_id not in self._nodes:
                event_type = ZwaveNodeAddedEvent
            # If the name has changed, we have a rename event
            elif node['name'] != self._nodes[node_id]['name']:
                event_type = ZwaveNodeRenamedEvent
            # If nothing relevant has changed, update the cached instance and return
            else:
                self._nodes[node_id] = node
                return

        evt = event_type(**kwargs)
        self._events_queue.put(evt)

        if (
            value
            and issubclass(event_type, ZwaveValueChangedEvent)
            and event_type != ZwaveValueRemovedEvent
        ):
            self.plugin.publish_entities([kwargs['value']])  # type: ignore

    def on_mqtt_message(self):
        def handler(_, __, msg):
            if not msg.topic.startswith(self.events_topic):
                return

            topic = (
                msg.topic[(len(self.events_topic) + 1) :].split('/').pop()  # noqa: E203
            )
            data = msg.payload.decode()
            if not data:
                return

            with contextlib.suppress(ValueError, TypeError):
                data = json.loads(data)['data']

            try:
                if topic == 'node_value_updated':
                    self._dispatch_event(
                        ZwaveValueChangedEvent, node=data[0], value=data[1]
                    )
                elif topic == 'node_metadata_updated':
                    self._dispatch_event(ZwaveNodeEvent, node=data[0])
                elif topic == 'node_sleep':
                    self._dispatch_event(ZwaveNodeAsleepEvent, node=data[0])
                elif topic == 'node_wakeup':
                    self._dispatch_event(ZwaveNodeAwakeEvent, node=data[0])
                elif topic == 'node_ready':
                    self._dispatch_event(ZwaveNodeReadyEvent, node=data[0])
                elif topic == 'node_removed':
                    self._dispatch_event(ZwaveNodeRemovedEvent, node=data[0])
            except Exception as e:
                self.logger.exception(e)

        return handler

    def run(self):
        super().run()
        self.logger.debug('Refreshing Z-Wave nodes')
        self._nodes = self.plugin.get_nodes().output  # type: ignore

        while not self.should_stop():
            try:
                evt = self._events_queue.get(block=True, timeout=1)
            except Empty:
                continue

            get_bus().post(evt)


# vim:sw=4:ts=4:et:
