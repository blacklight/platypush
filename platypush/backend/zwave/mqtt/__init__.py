import json
from queue import Queue, Empty
from typing import Optional, Type

from platypush.backend.mqtt import MqttBackend
from platypush.context import get_plugin

from platypush.message.event.zwave import ZwaveEvent, ZwaveNodeAddedEvent, ZwaveValueChangedEvent, \
    ZwaveNodeRemovedEvent, ZwaveNodeRenamedEvent, ZwaveNodeReadyEvent, ZwaveNodeEvent, ZwaveNodeAsleepEvent, \
    ZwaveNodeAwakeEvent


class ZwaveMqttBackend(MqttBackend):
    """
    Listen for events on a `zwavejs2mqtt <https://github.com/zwave-js/zwavejs2mqtt>`_ service.

    Triggers:

        * :class:`platypush.message.event.zwave.ZwaveNodeEvent` when a node attribute changes.
        * :class:`platypush.message.event.zwave.ZwaveNodeAddedEvent` when a node is added to the network.
        * :class:`platypush.message.event.zwave.ZwaveNodeRemovedEvent` when a node is removed from the network.
        * :class:`platypush.message.event.zwave.ZwaveNodeRenamedEvent` when a node is renamed.
        * :class:`platypush.message.event.zwave.ZwaveNodeReadyEvent` when a node is ready.
        * :class:`platypush.message.event.zwave.ZwaveValueChangedEvent` when the value of a node on the network
          changes.
        * :class:`platypush.message.event.zwave.ZwaveNodeAsleepEvent` when a node goes into sleep mode.
        * :class:`platypush.message.event.zwave.ZwaveNodeAwakeEvent` when a node goes back into awake mode.

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)
        * A `zwavejs2mqtt instance <https://github.com/zwave-js/zwavejs2mqtt>`_.
        * The :class:`platypush.plugins.zwave.mqtt.ZwaveMqttPlugin` plugin configured.

    """

    def __init__(self, client_id: Optional[str] = None, *args, **kwargs):
        """
        :param client_id: MQTT client ID (default: ``<device_id>-zwavejs-mqtt``, to prevent clashes with the
            :class:`platypush.backend.mqtt.MqttBackend` ``client_id``.
        """

        from platypush.plugins.zwave.mqtt import ZwaveMqttPlugin
        self.plugin: ZwaveMqttPlugin = get_plugin('zwave.mqtt')
        assert self.plugin, 'The zwave.mqtt plugin is not configured'

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

        listeners = [{
            **self.server_info,
            'topics': [
                self.plugin.events_topic + '/node/' + topic
                for topic in ['node_ready', 'node_sleep', 'node_value_updated', 'node_metadata_updated', 'node_wakeup']
            ],
        }]

        super().__init__(*args, subscribe_default_topic=False, listeners=listeners, client_id=client_id, **kwargs)
        if not client_id:
            self.client_id += '-zwavejs-mqtt'

    def _dispatch_event(self, event_type: Type[ZwaveEvent], node: Optional[dict] = None, value: Optional[dict] = None,
                        **kwargs):
        if value and 'id' not in value:
            value_id = f"{value['commandClass']}-{value.get('endpoint', 0)}-{value['property']}"
            if 'propertyKey' in value:
                value_id += '-' + str(value['propertyKey'])

            if value_id not in node.get('values', {}):
                self.logger.warning(f'value_id {value_id} not found on node {node["id"]}')
                return

            value = node['values'][value_id]

        if value:
            kwargs['value'] = self.plugin.value_to_dict(value)

        if node:
            kwargs['node'] = self.plugin.node_to_dict(node)
            node_id = kwargs['node']['node_id']

            if event_type == ZwaveNodeEvent:
                if node_id not in self._nodes:
                    event_type = ZwaveNodeAddedEvent
                elif kwargs['node']['name'] != self._nodes[node_id]['name']:
                    event_type = ZwaveNodeRenamedEvent

            if event_type == ZwaveNodeRemovedEvent:
                self._nodes.pop(node_id, None)
            else:
                self._nodes[node_id] = kwargs['node']

        evt = event_type(**kwargs)
        self._events_queue.put(evt)

        # zwavejs2mqtt currently treats some values (e.g. binary switches) in an inconsistent way,
        # using two values - a read-only value called currentValue that gets updated on the
        # node_value_updated topic, and a writable value called targetValue that doesn't get updated
        # (see https://github.com/zwave-js/zwavejs2mqtt/blob/4a6a5c5f1274763fd3aced4cae2c72ea060716b5/docs/guide/migrating.md).
        # To properly manage updates on writable values, propagate an event for both.
        if event_type == ZwaveValueChangedEvent and kwargs.get('value', {}).get('property_id') == 'currentValue':
            value = kwargs['value'].copy()
            target_value_id = f'{kwargs["node"]["node_id"]}-{value["command_class"]}-{value.get("endpoint", 0)}' \
                              f'-targetValue'
            kwargs['value'] = kwargs['node'].get('values', {}).get(target_value_id)

            if kwargs['value']:
                kwargs['value']['data'] = value['data']
                kwargs['node']['values'][target_value_id] = kwargs['value']
                evt = event_type(**kwargs)
                self._events_queue.put(evt)

    def on_mqtt_message(self):
        def handler(_, __, msg):
            if not msg.topic.startswith(self.events_topic):
                return

            topic = msg.topic[len(self.events_topic) + 1:].split('/').pop()
            data = msg.payload.decode()
            if not data:
                return

            try:
                data = json.loads(data)['data']
            except (ValueError, TypeError):
                pass

            try:
                if topic == 'node_value_updated':
                    self._dispatch_event(ZwaveValueChangedEvent, node=data[0], value=data[1])
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
        # noinspection PyUnresolvedReferences
        self._nodes = self.plugin.get_nodes().output

        while not self.should_stop():
            try:
                evt = self._events_queue.get(block=True, timeout=1)
            except Empty:
                continue

            self.bus.post(evt)


# vim:sw=4:ts=4:et:
