import json
import queue

from datetime import datetime
from threading import Timer
from typing import Optional, List, Any, Dict, Union, Iterable, Callable

from platypush.message.event.zwave import ZwaveNodeRenamedEvent, ZwaveNodeEvent

from platypush.context import get_backend, get_bus
from platypush.message.response import Response
from platypush.plugins.mqtt import MqttPlugin, action
from platypush.plugins.zwave._base import ZwaveBasePlugin
from platypush.plugins.zwave._constants import command_class_by_name

_NOT_IMPLEMENTED_ERR = NotImplementedError('Not implemented by zwave.mqtt')


class ZwaveMqttPlugin(MqttPlugin, ZwaveBasePlugin):
    """
    This plugin allows you to manage a Z-Wave network over MQTT through
    `zwavejs2mqtt <https://github.com/zwave-js/zwavejs2mqtt>`_.

    Configuration required on the zwavejs2mqtt gateway:

        * Install the gateway following the instructions reported
          `here <https://zwave-js.github.io/zwavejs2mqtt/#/getting-started/quick-start>`_.

        * Configure the following settings from the zwavejs2mqtt web panel:

            * Zwave -> Serial Port: The path to your Z-Wave adapter.
            * Disabled MQTT Gateway: Set to false.
            * Configure the MQTT server that should be used by the service.
            * Mqtt -> Name: Unique name that identifies your gateway.
            * Mqtt -> Prefix: Prefix name for the topics published to MQTT.
            * Gateway -> Topic type: Set to "ValueID topics".
            * Gateway -> Payload type: Set to "JSON Time-Value".
            * Gateway -> Use nodes name instead of numeric nodeIDs: Set to false.
            * Gateway -> Send Zwave Events: Set to true.
            * Gateway -> Include Node Info: Set to true.

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)

    """

    def __init__(self, name: str, host: str = 'localhost', port: int = 1883, topic_prefix: str = 'zwave',
                 timeout: int = 10, tls_certfile: Optional[str] = None, tls_keyfile: Optional[str] = None,
                 tls_version: Optional[str] = None, tls_ciphers: Optional[str] = None, username: Optional[str] = None,
                 password: Optional[str] = None, **kwargs):
        """
        :param name: Gateway name, as configured from the zwavejs2mqtt web panel from Mqtt -> Name.
        :param host: MQTT broker host, as configured from the zwavejs2mqtt web panel from Mqtt -> Host
            (default: ``localhost``).
        :param port: MQTT broker listen port, as configured from the zwavejs2mqtt web panel from Mqtt -> Port
            (default: 1883).
        :param topic_prefix: MQTT topic prefix, as specified from the zwavejs2mqtt web panel from Mqtt -> Prefix
            (default: ``zwave``).
        :param timeout: If the command expects from a response, then this timeout value will be used
            (default: 60 seconds).
        :param tls_cafile: If the connection requires TLS/SSL, specify the certificate authority file
            (default: None)
        :param tls_certfile: If the connection requires TLS/SSL, specify the certificate file (default: None)
        :param tls_keyfile: If the connection requires TLS/SSL, specify the key file (default: None)
        :param tls_version: If the connection requires TLS/SSL, specify the minimum TLS supported version
            (default: None)
        :param tls_ciphers: If the connection requires TLS/SSL, specify the supported ciphers (default: None)
        :param username: If the connection requires user authentication, specify the username (default: None)
        :param password: If the connection requires user authentication, specify the password (default: None)
        """

        super().__init__(host=host, port=port, tls_certfile=tls_certfile, tls_keyfile=tls_keyfile,
                         tls_version=tls_version, tls_ciphers=tls_ciphers, username=username,
                         password=password, **kwargs)

        self.topic_prefix = topic_prefix
        self.base_topic = topic_prefix + '/{}/ZWAVE_GATEWAY-' + name
        self.events_topic = self.base_topic.format('_EVENTS')
        self.timeout = timeout
        self._info = {
            'devices': {},
            'groups': {},
        }

        self._nodes_cache = {
            'by_id': {},
            'by_name': {},
        }

        self._values_cache = {
            'by_id': {},
            'by_label': {},
        }

        self._scenes_cache = {
            'by_id': {},
            'by_label': {},
        }

        self._groups_cache = {}

    @staticmethod
    def _get_backend():
        backend = get_backend('zwave.mqtt')
        if not backend:
            raise AssertionError('zwave.mqtt backend not configured')
        return backend

    def _api_topic(self, api: str) -> str:
        return self.base_topic.format('_CLIENTS') + '/api/{}'.format(api)

    def _topic(self, topic):
        return self.base_topic + '/' + topic

    @staticmethod
    def _parse_response(response: Union[dict, Response]) -> dict:
        if isinstance(response, Response):
            response = response.output

        assert response.get('success') is True, response.get('message', 'zwavejs2mqtt error')
        return response

    def _api_request(self, api: str, *args, **kwargs):
        payload = json.dumps({'args': args})
        ret = self._parse_response(
            self.publish(topic=self._api_topic(api) + '/set', msg=payload, reply_topic=self._api_topic(api),
                         **self._mqtt_args(**kwargs)))

        assert not ret or ret.get('success') is True, ret.get('message')
        return ret.get('result')

    @staticmethod
    def _convert_timestamp(t: Optional[int]) -> Optional[datetime]:
        if t:
            return datetime.fromtimestamp(t / 1000)

    def _get_scene(self, scene_id: Optional[int] = None, scene_label: Optional[str] = None, **kwargs) -> dict:
        assert scene_id or scene_label, 'No scene_id/scene_label specified'
        if scene_id in self._scenes_cache['by_id']:
            return self._scenes_cache['by_id'][scene_id]
        if scene_label in self._scenes_cache['by_label']:
            return self._scenes_cache['by_label'][scene_label]

        # noinspection PyUnresolvedReferences
        scenes = self.get_scenes(**kwargs).output
        scene = None

        if scene_id in scenes:
            scene = scenes[scene_id]
            self._scenes_cache['by_id'][scene_id] = scene
        else:
            scenes = [s for s in scenes if s['label'] == scene_label]
            if scenes:
                scene = scenes[0]
                self._scenes_cache['by_label'][scene_label] = scene

        assert scene, f'No such scene: scene_id={scene_id}, scene_label={scene_label}'
        return scene

    @classmethod
    def group_to_dict(cls, group: dict, node_id: Optional[int] = None) -> dict:
        return {
            'label': group['text'],
            'index': group['value'],
            'node_id': node_id,
            'group_id': f'{node_id}:{group["value"]}' if node_id is not None else None,
            'multichannel': group['multiChannel'],
            'max_associations': group['maxNodes'],
        }

    @classmethod
    def _get_type(cls, value: dict) -> str:
        if value['list']:
            if len(value.get('states', [])) > 1:
                return 'List'
            if value.get('min') is not None and value.get('max') is not None:
                return 'Decimal'
        if value['type'] == 'boolean':
            return 'Bool'
        if value['type'] == 'number':
            return 'Decimal'
        if value['type'] == 'string':
            return 'String'
        return value['type'].capitalize()

    @classmethod
    def value_to_dict(cls, value: dict) -> dict:
        return {
            'id': value['id'],
            'id_on_network': value['id'],
            'value_id': value['id'],
            'data': value.get('value'),
            'data_items': [state for state in value['states']] if len(value.get('states', [])) > 1 else None,
            'label': value.get('label', value.get('propertyName', value.get('property'))),
            'property_id': value.get('property'),
            'help': value.get('description'),
            'node_id': value.get('nodeId'),
            'parent_id': value.get('nodeId'),
            'type': cls._get_type(value),
            'default': value.get('default'),
            'endpoint': value.get('endpoint'),
            'stateless': value.get('stateless'),
            'command_class': value.get('commandClass'),
            'command_class_name': value.get('commandClassName'),
            'units': value.get('unit'),
            'min': value.get('min'),
            'max': value.get('max'),
            'is_read_only': value['readable'] and not value['writeable'],
            'is_write_only': value['writeable'] and not value['readable'],
            'last_update': cls._convert_timestamp(value.get('lastUpdate')),
            **({'property_key': value['propertyKey']} if 'propertyKey' in value else {}),
            **({'property_key_name': value['propertyKeyName']} if 'propertyKeyName' in value else {}),
        }

    @staticmethod
    def _get_value_id(value: dict) -> str:
        return f'{value["nodeId"]}-{value["commandClass"]}-{value.get("endpoint", 0)}-{value["property"]}'

    @classmethod
    def scene_to_dict(cls, scene: dict) -> dict:
        return {
            'scene_id': scene.pop('sceneid', None),
            'values': {
                cls._get_value_id(value): {
                    'node_id': value['nodeId'],
                    'value_id': cls._get_value_id(value),
                    'id_on_network': cls._get_value_id(value),
                    'data': value.get('value'),
                }
                for value in scene.pop('values', [])
            },
            **scene,
        }

    @classmethod
    def node_to_dict(cls, node: dict) -> dict:
        capabilities = []
        if node['supportsBeaming']:
            capabilities += ['beaming']
        if node['supportsSecurity']:
            capabilities += ['security']
        if node['isRouting']:
            capabilities += ['routing']
        if node.get('zwavePlusVersion'):
            capabilities += ['zwave_plus']

        return {
            'node_id': node['id'],
            'device_id': node['hexId'].replace('0x', ''),
            'name': node.get('name'),
            'capabilities': capabilities,
            'manufacturer_id': '0x{:04x}'.format(node['manufacturerId']) if node.get('manufacturerId') else None,
            'manufacturer_name': node.get('manufacturer'),
            'location': node.get('loc'),
            'status': node.get('status'),
            'is_available': node.get('available'),
            'is_awake': node.get('ready') and node.get('status') != 'Asleep',
            'is_beaming_device': node.get('supportsBeaming'),
            'is_controller': node.get('isControllerNode'),
            'is_failed': node.get('failed'),
            'is_frequent_listening_device': node.get('isFrequentListening'),
            'is_info_received': node.get('interviewStage') == 'Complete',
            'is_initialized': node.get('inited'),
            'is_listening_device': node.get('isListening'),
            'is_ready': node.get('ready'),
            'is_routing_device': node.get('isRouting'),
            'is_security_device': node.get('supportsSecurity'),
            'is_sleeping': node.get('ready') and node.get('status') == 'Asleep',
            'last_update': cls._convert_timestamp(node.get('lastActive')),
            'product_id': '0x{:04x}'.format(node['productId']) if node.get('productId') else None,
            'product_type': '0x{:04x}'.format(node['productType']) if node.get('productType') else None,
            'product_name': ' '.join([node.get('productLabel', ''), node.get('productDescription', '')]),
            'baud_rate': node.get('dataRate'),
            'max_baud_rate': node.get('maxBaudRate', node.get('dataRate')),
            'device_class': node.get('deviceClass'),
            'specific': node.get('deviceClass', {}).get('specific'),
            'firmware_version': node.get('firmwareVersion'),
            'keep_awake': node.get('keepAwake'),
            'db_link': node.get('dbLink'),
            'type': node.get('zwavePlusNodeType'),
            'role': node.get('zwavePlusRoleType'),
            'zwave_plus_version': node.get('zwavePlusVersion'),
            'zwave_plus_node_type': node.get('zwavePlusNodeType'),
            'zwave_plus_role_type': node.get('zwavePlusRoleType'),
            'neighbours': node.get('neighbors', []),

            'command_classes': {
                value['commandClassName']
                for value in node.get('values', {}).values() if value.get('commandClassName')
            },

            'groups': {
                group['value']: cls.group_to_dict(group, node_id=node['id'])
                for group in node.get('groups', [])
            },

            'values': {
                value['id']: cls.value_to_dict(value)
                for value in node.get('values', {}).values()
            },
        }

    def _get_node(self, node_id: Optional[int] = None, node_name: Optional[str] = None, use_cache: bool = True,
                  **kwargs) -> Optional[dict]:
        assert node_id or node_name, 'Please provide either a node_id or node_name'
        if use_cache:
            if node_id and node_id in self._nodes_cache['by_id']:
                return self._nodes_cache['by_id'][node_id]
            if node_name and node_name in self._nodes_cache['by_name']:
                return self._nodes_cache['by_name'][node_name]

        response = {
            node['id']: self.node_to_dict(node)
            for node in self._api_request('getNodes', **kwargs)
        }

        node = None
        if node_id:
            node = response.get(node_id)
        else:
            ret = [node for node in response.values() if node['name'] == node_name]
            if ret:
                node = ret[0]

        if node:
            self._nodes_cache['by_id'][node['node_id']] = node
            if node['name']:
                self._nodes_cache['by_name'][node['name']] = node

            for value in node.get('values', {}).values():
                self._values_cache['by_id'][value['id']] = value
                if value['label']:
                    self._values_cache['by_label'][value['label']] = value

        return node

    def _get_value(self, value_id: Optional[int] = None, id_on_network: Optional[str] = None,
                   value_label: Optional[str] = None, node_id: Optional[int] = None, node_name: Optional[str] = None,
                   use_cache: bool = True, **_) -> Dict[str, Any]:
        # Unlike python-openzwave, value_id and id_on_network are the same on zwavejs2mqtt
        value_id = value_id or id_on_network
        assert value_id or value_label, 'Please provide either value_id, id_on_network or value_label'

        if use_cache:
            if value_id and value_id in self._values_cache['by_id']:
                return self._values_cache['by_id'][value_id]
            if value_label and value_label in self._values_cache['by_label']:
                return self._values_cache['by_label'][value_label]

        nodes = []
        if node_id or node_name:
            nodes = [self._get_node(node_id=node_id, node_name=node_name, use_cache=False)]

        if not nodes:
            # noinspection PyUnresolvedReferences
            nodes = self.get_nodes().output
            assert nodes, 'No nodes found on the network'
            nodes = nodes.values()

        if value_id:
            values = [
                node['values'][value_id]
                for node in nodes
                if value_id in node.get('values', {})
            ]
        else:
            values = [
                value
                for node in nodes
                for value in node.get('values', {}).values()
                if value.get('label') == value_label
            ]

        assert values, f'No such value: {value_id or value_label}'
        value = values[0]

        if value.get('property_id') == 'targetValue':
            cur_value_id = '-'.join(value['value_id'].split('-')[:-1] + ['currentValue'])
            cur_value = self._nodes_cache['by_id'][value['node_id']].get('values', {}).get(cur_value_id)
            if cur_value:
                value['data'] = cur_value['data']

        self._values_cache['by_id'][value['id']] = value
        if value['label']:
            self._values_cache['by_label'][value['label']] = value

        return value

    def _topic_by_value_id(self, value_id: str) -> str:
        return self.topic_prefix + '/' + '/'.join(value_id.split('-'))

    def _filter_values(self, command_classes: Iterable[str], filter_callback: Optional[Callable[[dict], bool]] = None,
                       node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        # noinspection PyUnresolvedReferences
        nodes = [self._get_node(node_name=node_name, use_cache=False, **kwargs)] if node_id or node_name else \
            self.get_nodes(**kwargs).output.values()

        command_classes = {
            command_class_by_name[command_name]
            for command_name in command_classes
        }

        values = {}

        for node in nodes:
            for value in node.get('values', {}).values():
                if value.get('command_class') not in command_classes or (
                        filter_callback and not filter_callback(value)):
                    continue

                value_id = value['id_on_network']
                if value_id.split('-').pop() == 'targetValue':
                    value_id = '-'.join(value_id.split('-')[:-1]) + '-currentValue'
                    cur_value = self._nodes_cache['by_id'][value['node_id']].get('values', {}).get(value_id)
                    if cur_value:
                        value['data'] = cur_value['data']

                values[value['id_on_network']] = value

        return values

    def _get_group(self, group_id: Optional[str] = None, group_index: Optional[int] = None, **kwargs) -> dict:
        group_id = group_id or group_index
        assert group_id is not None, 'No group_id/group_index specified'
        group = self._groups_cache.get(group_id)
        if group:
            return group

        # noinspection PyUnresolvedReferences
        groups = self.get_groups(**kwargs).output
        assert group_id in groups, f'No such group_id: {group_id}'
        return groups[group_id]

    @action
    def start_network(self, **kwargs):
        """
        Start the network (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def stop_network(self, **kwargs):
        """
        Stop the network (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def status(self, **kwargs) -> Dict[str, Any]:
        """
        Get the status of the controller.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        :return: dict with the following fields: ``device`` and ``state``.
        """
        msg_queue = queue.Queue()
        topic = f'{self.topic_prefix}/Controller/status'
        client = self._get_client(**kwargs)

        def on_message(_, __, msg):
            if msg.topic != topic:
                return
            msg_queue.put(json.loads(msg.payload))

        client.on_message = on_message
        client.connect(kwargs.get('host', self.host), kwargs.get('port', self.port),
                       keepalive=kwargs.get('timeout', self.timeout))

        client.subscribe(topic)
        client.loop_start()

        try:
            status = msg_queue.get(block=True, timeout=kwargs.get('timeout', self.timeout))
        except queue.Empty:
            raise TimeoutError('The request timed out')
        finally:
            client.loop_stop()

        return {
            'device': status['nodeId'],
            'state': status['status'],
            'stats': {},
        }

    @action
    def add_node(self, do_security: bool = False, timeout: int = 60, **kwargs):
        """
        Start the inclusion process to add a node to the network.

        :param do_security: Whether to initialize the Network Key on the device if it supports the Security CC
        :param timeout: How long the inclusion process should last, in seconds (default: 60). Specify zero or null
            for no timeout.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self._api_request('startInclusion', **kwargs)
        if timeout:
            Timer(timeout, lambda: self._api_request('stopInclusion', **kwargs)).start()

    @action
    def remove_node(self, **kwargs):
        """
        Remove a node from the network (not implemented on zwavejs2mqtt).

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def remove_failed_node(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Remove a failed node from the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_name:
            node_id = (self._get_node(node_name=node_name) or {}).get('node_id')

        assert node_id is not None, f'No such node_id: {node_id}'
        self._api_request('removeFailedNode', node_id, **kwargs)

    @action
    def replace_failed_node(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Replace a failed node on the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_name:
            node_id = (self._get_node(node_name=node_name) or {}).get('node_id')

        assert node_id is not None, f'No such node_id: {node_id}'
        self._api_request('replaceFailedNode', node_id, **kwargs)

    @action
    def replication_send(self, **kwargs):
        """
        Send node information from the primary to the secondary controller (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def request_network_update(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Request a network update to a node.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_name:
            node_id = (self._get_node(node_name=node_name) or {}).get('node_id')

        assert node_id is not None, f'No such node_id: {node_id}'
        self._api_request('refreshInfo', node_id, **kwargs)

    @action
    def request_node_neighbour_update(self, **kwargs):
        """
        Request a neighbours list update.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self._api_request('refreshNeighbors', **kwargs)

    @action
    def get_nodes(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) \
            -> Optional[Dict[str, Any]]:
        """
        Get the nodes associated to the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).

        :return: List of paired devices. Example output:

            .. code-block:: json

                {
                  "1": {
                    "node_id": 1,
                    "device_id": "0115-0400-0001",
                    "name": "Controller",
                    "capabilities": [
                      "beaming",
                      "routing"
                    ],
                    "manufacturer_id": "0x0115",
                    "manufacturer_name": "Z-Wave.Me",
                    "location": "Living Room",
                    "status": "Alive",
                    "is_available": true,
                    "is_awake": true,
                    "is_beaming_device": true,
                    "is_controller": true,
                    "is_failed": false,
                    "is_frequent_listening_device": false,
                    "is_info_received": true,
                    "is_initialized": true,
                    "is_listening_device": true,
                    "is_ready": true,
                    "is_routing_device": true,
                    "is_security_device": false,
                    "is_sleeping": false,
                    "last_update": "2021-04-05T19:38:07.202000",
                    "product_id": null,
                    "product_type": null,
                    "product_name": "UZB Z-Wave USB Stick",
                    "baud_rate": 100000,
                    "max_baud_rate": null,
                    "device_class": {
                      "basic": 2,
                      "generic": 2,
                      "specific": 1
                    },
                    "specific": 1,
                    "firmware_version": null,
                    "keep_awake": false,
                    "db_link": "https://devices.zwave-js.io/?jumpTo=0x0115:0x0400:0x0001:0.0",
                    "zwave_plus_version": null,
                    "zwave_plus_node_type": null,
                    "zwave_plus_role_type": null,
                    "neighbours": [
                      3,
                      4
                    ],
                    "groups": {},
                    "values": {}
                  },
                  "4": {
                    "node_id": 4,
                    "device_id": "010f-0602-1003",
                    "name": "TV Switch",
                    "capabilities": [
                      "beaming",
                      "routing",
                      "zwave_plus"
                    ],
                    "manufacturer_id": "0x010f",
                    "manufacturer_name": "Fibargroup",
                    "location": "Living Room",
                    "status": "Alive",
                    "is_available": true,
                    "is_awake": true,
                    "is_beaming_device": true,
                    "is_controller": false,
                    "is_failed": false,
                    "is_frequent_listening_device": false,
                    "is_info_received": true,
                    "is_initialized": true,
                    "is_listening_device": true,
                    "is_ready": true,
                    "is_routing_device": true,
                    "is_security_device": false,
                    "is_sleeping": false,
                    "last_update": "2021-04-06T00:07:44.081000",
                    "product_id": null,
                    "product_type": null,
                    "product_name": "Metered Wall Plug Switch",
                    "baud_rate": 100000,
                    "max_baud_rate": null,
                    "device_class": {
                      "basic": 4,
                      "generic": 16,
                      "specific": 1
                    },
                    "specific": 1,
                    "firmware_version": "3.2",
                    "keep_awake": false,
                    "db_link": "https://devices.zwave-js.io/?jumpTo=0x010f:0x0602:0x1003:3.2",
                    "zwave_plus_version": 1,
                    "zwave_plus_node_type": 0,
                    "zwave_plus_role_type": 5,
                    "neighbours": [
                      1
                    ],
                    "groups": {
                      "1": {
                        "label": "Lifeline",
                        "index": 1,
                        "multichannel": true,
                        "max_associations": 1
                      },
                      "2": {
                        "label": "On/Off (Button)",
                        "index": 2,
                        "multichannel": true,
                        "max_associations": 10
                      },
                      "3": {
                        "label": "On/Off (Power)",
                        "index": 3,
                        "multichannel": true,
                        "max_associations": 10
                      }
                    },
                    "values": {
                      "4-37-0-currentValue": {
                        "id": "4-37-0-currentValue",
                        "id_on_network": "4-37-0-currentValue",
                        "value_id": "4-37-0-currentValue",
                        "data": true,
                        "data_items": null,
                        "label": "Current value",
                        "property_id": "currentValue",
                        "help": null,
                        "node_id": 4,
                        "parent_id": 4,
                        "type": "Bool",
                        "default": null,
                        "endpoint": 0,
                        "stateless": false,
                        "command_class": 37,
                        "command_class_name": "Binary Switch",
                        "units": null,
                        "min": null,
                        "max": null,
                        "is_read_only": true,
                        "is_write_only": false,
                        "last_update": "2021-04-05T19:38:07.587000"
                      }
                    }
                  }
                }

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_id or node_name:
            return self._get_node(node_id=node_id, node_name=node_name, use_cache=False, **kwargs)

        nodes = {
            node['id']: self.node_to_dict(node)
            for node in self._api_request('getNodes', **kwargs)
        }

        self._nodes_cache['by_id'] = nodes
        self._nodes_cache['by_name'] = {
            node['name']: node
            for node in nodes.values()
        }

        return nodes

    @action
    def get_node_stats(self, **kwargs):
        """
        Get the statistics of a node on the network (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def set_node_name(self, new_name: str, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Rename a node on the network.

        :param new_name: New name for the node.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')

        assert node_id, f'No such node: {node_id}'
        self._api_request('setNodeName', node_id, new_name, **kwargs)
        get_bus().post(ZwaveNodeRenamedEvent(node={
            **self._get_node(node_id=node_id),
            'name': new_name,
        }))

    @action
    def set_node_product_name(self, **kwargs):
        """
        Set the product name of a node (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def set_node_manufacturer_name(self, **kwargs):
        """
        Set the manufacturer name of a node (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def set_node_location(self, location: str, node_id: Optional[int] = None, node_name: Optional[str] = None,
                          **kwargs):
        """
        Set the location of a node.

        :param location: Node location.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')

        assert node_id, f'No such node: {node_id}'
        self._api_request('setNodeLocation', node_id, location, **kwargs)
        get_bus().post(ZwaveNodeEvent(node={
            **self._get_node(node_id=node_id),
            'location': location,
        }))

    @action
    def cancel_command(self, **kwargs):
        """
        Cancel the current running command (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def kill_command(self, **kwargs):
        """
        Immediately terminate any running command on the controller and release the lock (not implemented by
        zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def set_controller_name(self, **kwargs):
        """
        Set the name of the controller on the network (not implemented: use
        :meth:`platypush.plugin.zwave.mqtt.ZwaveMqttPlugin.set_node_name` instead).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def get_capabilities(self, **kwargs) -> List[str]:
        """
        Get the capabilities of the controller (not implemented: use
        :meth:`platypush.plugin.zwave.mqtt.ZwaveMqttPlugin.get_nodes` instead).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def receive_configuration(self, **kwargs):
        """
        Receive the configuration from the primary controller on the network. Requires a primary controller active
        (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def transfer_primary_role(self, **kwargs):
        """
        Add a new controller to the network and make it the primary.
        The existing primary will become a secondary controller (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def heal(self, timeout: Optional[int] = 60, **kwargs):
        """
        Heal network by requesting nodes rediscover their neighbours.

        :param timeout: Duration of the healing process in seconds (default: 60). Set to zero or null for no timeout.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self._api_request('beginHealingNetwork', **kwargs)
        if timeout:
            Timer(timeout, lambda: self._api_request('stopHealingNetwork', **kwargs)).start()

    @action
    def switch_all(self, **kwargs):
        """
        Switch all the connected devices on/off (not implemented).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def test(self, count: int = 1, **kwargs):
        """
        Send a number of test messages to every node and record results (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def get_value(self, value_id: Optional[int] = None, id_on_network: Optional[str] = None,
                  value_label: Optional[str] = None, node_id: Optional[int] = None, node_name: Optional[str] = None,
                  **kwargs) -> Dict[str, Any]:
        """
        Get a value on the network.

        :param value_id: Select by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._get_value(value_id=value_id, value_label=value_label, id_on_network=id_on_network, node_id=node_id,
                               node_name=node_name, use_cache=False, **kwargs)

    @action
    def set_value(self, data, value_id: Optional[int] = None, id_on_network: Optional[str] = None,
                  value_label: Optional[str] = None, node_id: Optional[int] = None, node_name: Optional[str] = None,
                  **kwargs):
        """
        Set a value.

        :param data: Data to set for the value.
        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        value = self._get_value(value_id=value_id, value_label=value_label, id_on_network=id_on_network,
                                node_id=node_id, node_name=node_name, **kwargs)

        self._api_request('writeValue', {
            'nodeId': value['node_id'],
            'commandClass': value['command_class'],
            'endpoint': value.get('endpoint', 0),
            'property': value['property_id'],
            **({'propertyKey': value['property_key']} if 'property_key' in value else {}),
        }, data, **kwargs)

    @action
    def set_value_label(self, **kwargs):
        """
        Change the label/name of a value (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def node_add_value(self, **kwargs):
        """
        Add a value to a node (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def node_remove_value(self, **kwargs):
        """
        Remove a value from a node (not implemented by zwavejs2mqtt).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def node_heal(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Heal network node by requesting the node to rediscover their neighbours.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')
        self._api_request('healNode', node_id, **kwargs)

    @action
    def node_update_neighbours(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Ask a node to update its neighbours table
        (same as :meth:`platypush.plugins.zwave.mqtt.ZwaveMqttPlugin.node_heal`).

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.node_heal(node_id=node_id, node_name=node_name, **kwargs)

    @action
    def node_network_update(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Update the controller with network information
        (same as :meth:`platypush.plugins.zwave.mqtt.ZwaveMqttPlugin.node_heal`).

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.node_heal(node_id=node_id, node_name=node_name, **kwargs)

    @action
    def node_refresh_info(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Fetch up-to-date information about the node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')
        self._api_request('refreshInfo', node_id, **kwargs)

    @action
    def get_dimmers(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the dimmers on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['switch_multilevel', 'switch_toggle_multilevel'], node_id=node_id,
                                   node_name=node_name, **kwargs)

    @action
    def get_node_config(self, node_id: Optional[int] = None, node_name: Optional[str] = None,
                        **kwargs) -> Dict[str, Any]:
        """
        Get the configuration values of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['configuration', 'ip_configuration', 'association_command_configuration',
                                    'sensor_configuration'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_battery_levels(self, node_id: Optional[int] = None, node_name: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """
        Get the battery levels of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['battery'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_power_levels(self, node_id: Optional[int] = None, node_name: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Get the power levels of this node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['powerlevel'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_bulbs(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the bulbs/LEDs on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['color'], filter_callback=lambda value: not value['is_read_only'], node_id=node_id,
                                   node_name=node_name, **kwargs)

    @action
    def get_switches(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the switches on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['switch_binary', 'switch_toggle_binary'],
                                   filter_callback=lambda value: not value['is_read_only'],
                                   node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_sensors(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the sensors on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['sensor_binary', 'sensor_multilevel', 'sensor_alarm', 'meter'],
                                   filter_callback=lambda value: not value['is_write_only'],
                                   node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_doorlocks(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the doorlocks on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['door_lock'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_locks(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the locks on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['lock'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_usercodes(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the usercodes on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['user_code'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_thermostats(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) \
            -> Dict[str, Any]:
        """
        Get the thermostats on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['thermostat_heating', 'thermostat_mode', 'thermostat_operating_state',
                                    'thermostat_setpoint', 'thermostat_fan_mode', 'thermostat_fan_state',
                                    'thermostat_setback'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_protections(self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs) \
            -> Dict[str, Any]:
        """
        Get the protection-compatible devices on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._filter_values(['protection'], node_id=node_id, node_name=node_name, **kwargs)

    @action
    def get_groups(self, **kwargs) -> Dict[str, dict]:
        """
        Get the groups on the network.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).

        :return: A list of the available groups. Example:

          .. code-block:: json

            {
              "2-2": {
                "label": "Motion",
                "multichannel": true,
                "max_associations": 10,
                "group_id": "2-2",
                "node_id": 2,
                "index": 2,
                "associations": [
                  3,
                  4
                ]
              },
              "5-3": {
                "label": "Tamper",
                "multichannel": true,
                "max_associations": 10,
                "group_id": "5-3",
                "node_id": 5,
                "index": 3,
                "associations": [
                  2,
                  3,
                  4
                ]
              }
            ]

        """
        # noinspection PyUnresolvedReferences
        nodes = self.get_nodes(**kwargs).output
        self._groups_cache = {
            group['group_id']: {
                **group,
                'associations': [
                    assoc['nodeId'] for assoc in self._api_request('getAssociations', node_id, group['index'])
                ],
            }
            for node_id, node in nodes.items()
            for group in node.get('groups', {}).values()
        }

        return self._groups_cache

    @action
    def get_scenes(self, **kwargs) -> Dict[int, Dict[str, Any]]:
        """
        Get the scenes configured on the network.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        :return: dict with the following format:

          .. code-block:: json

            {
              1: {
                "scene_id": 1,
                "label": "Scene 1",
                "values": {
                  "4-37-0-targetValue": {
                     "node_id": 4,
                     "value_id": "4-37-0-targetValue"
                     "data": true
                  },
                  "3-112-0-Temperature": {
                    "node_id": 3,
                    "value_id": "3-112-0-Temperature",
                    "data": true
                  }
                }
              }
            }

        """
        return {
            scene.get('sceneid'): self.scene_to_dict(scene)
            for scene in self._api_request('_getScenes')
        }

    @action
    def create_scene(self, label: str, **kwargs):
        """
        Create a new scene.

        :param label: Scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self._api_request('_createScene', label)

    @action
    def remove_scene(self, scene_id: Optional[int] = None, scene_label: Optional[str] = None, **kwargs):
        """
        Remove a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        self._api_request('_removeScene', scene['scene_id'])

    @action
    def activate_scene(self, scene_id: Optional[int] = None, scene_label: Optional[str] = None, **kwargs):
        """
        Activate a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        self._api_request('_activateScene', scene['scene_id'])

    @action
    def set_scene_label(self, new_label: str, scene_id: Optional[int] = None, scene_label: Optional[str] = None,
                        **kwargs):
        """
        Rename a scene/set the scene label.

        :param new_label: New label.
        :param scene_id: Select by scene_id.
        :param scene_label: Select by current scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def scene_add_value(self, data: Optional[Any] = None, value_id: Optional[int] = None,
                        id_on_network: Optional[str] = None, value_label: Optional[str] = None,
                        scene_id: Optional[int] = None, scene_label: Optional[str] = None,
                        node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs):
        """
        Add a value to a scene.

        :param data: Data to set for the value (default: current value data).
        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param scene_id: Select scene by scene_id.
        :param scene_label: Select scene by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        value = self._get_value(value_id=value_id, value_label=value_label, id_on_network=id_on_network,
                                node_id=node_id, node_name=node_name, **kwargs)
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)

        self._api_request('_addSceneValue', scene['scene_id'], {
            'nodeId': value['node_id'],
            'commandClass': value['command_class'],
            'property': value['property_id'],
            'endpoint': value['endpoint'],
        }, data, kwargs.get('timeout', self.timeout))

    @action
    def scene_remove_value(self, value_id: Optional[int] = None, id_on_network: Optional[str] = None,
                           value_label: Optional[str] = None, scene_id: Optional[int] = None,
                           scene_label: Optional[str] = None, node_id: Optional[int] = None,
                           node_name: Optional[str] = None, **kwargs):
        """
        Remove a value from a scene.

        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param scene_id: Select scene by scene_id.
        :param scene_label: Select scene by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        value = self._get_value(value_id=value_id, value_label=value_label, id_on_network=id_on_network,
                                node_id=node_id, node_name=node_name, **kwargs)
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        self._api_request('_removeSceneValue', scene['scene_id'], value['value_id'])

    @action
    def get_scene_values(self, scene_id: Optional[int] = None, scene_label: Optional[str] = None, **kwargs) -> dict:
        """
        Get the values associated to a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        return scene.get('values', {})

    @action
    def create_button(self, button_id: Union[int, str], node_id: Optional[int] = None, node_name: Optional[str] = None,
                      **kwargs):
        """
        Create a handheld button on a device. Only intended for bridge firmware controllers
        (not implemented by zwavejs2mqtt).

        :param button_id: The ID of the button.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def delete_button(self, button_id: Union[int, str], node_id: Optional[int] = None, node_name: Optional[str] = None,
                      **kwargs):
        """
        Delete a button association from a device. Only intended for bridge firmware controllers.
        (not implemented by zwavejs2mqtt).

        :param button_id: The ID of the button.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def add_node_to_group(self, group_id: Optional[str] = None, node_id: Optional[int] = None,
                          endpoint: Optional[int] = None, **kwargs):
        """
        Add a node to a group.

        :param group_id: Group ID.
        :param node_id: Node ID to be added.
        :param endpoint: Add a specific endpoint of the node to the group (default: add a node association).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        group = self._get_group(group_id, **kwargs)
        assoc = {'nodeId': node_id}
        if endpoint is not None:
            assoc['endpoint'] = endpoint

        self._api_request('addAssociations', group['node_id'], group['index'], [assoc])

    @action
    def remove_node_from_group(self, group_id: Optional[str] = None, node_id: Optional[int] = None,
                               endpoint: Optional[int] = None, **kwargs):
        """
        Remove a node from a group.

        :param group_id: Group ID.
        :param node_id: Node ID to be added.
        :param endpoint: Node endpoint to remove (default: remove node association).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        group = self._get_group(group_id, **kwargs)
        assoc = {'nodeId': node_id}
        if endpoint is not None:
            assoc['endpoint'] = endpoint

        self._api_request('removeAssociations', group['node_id'], group['index'], [assoc])

    @action
    def create_new_primary(self, **kwargs):
        """
        Create a new primary controller on the network when the previous primary fails
        (not implemented by zwavejs2mqtt).

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def hard_reset(self, **kwargs):
        """
        Perform a hard reset of the controller. It erases its network configuration settings.
        The controller becomes a primary controller ready to add devices to a new network.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self._api_request('hardReset')

    @action
    def soft_reset(self, **kwargs):
        """
        Perform a soft reset of the controller.
        Resets a controller without erasing its network configuration settings (not implemented by zwavejs2).

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def write_config(self, **kwargs):
        """
        Store the current configuration of the network to the user directory (not implemented by zwavejs2mqtt).

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        raise _NOT_IMPLEMENTED_ERR

    @action
    def on(self, device: str, *args, **kwargs):
        """
        Turn on a switch on a device.

        :param device: ``id_on_network`` of the value to be switched on.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.set_value(data=True, id_on_network=device, **kwargs)

    @action
    def off(self, device: str, *args, **kwargs):
        """
        Turn off a switch on a device.

        :param device: ``id_on_network`` of the value to be switched off.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.set_value(data=False, id_on_network=device, **kwargs)

    @action
    def toggle(self, device: str, *args, **kwargs) -> dict:
        """
        Toggle a switch on a device.

        :param device: ``id_on_network`` of the value to be toggled.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        value = self._get_value(id_on_network=device, use_cache=False, **kwargs)
        value['data'] = not value['data']
        self.set_value(data=value['data'], id_on_network=device, **kwargs)

        return {
            'name': '{} - {}'.format(self._nodes_cache['by_id'][value['node_id']]['name'],
                                     value.get('label', '[No Label]')),
            'on': value['data'],
            'id': value['value_id'],
        }

    @property
    def switches(self) -> List[dict]:
        # Repopulate the nodes cache
        self.get_nodes()
        # noinspection PyUnresolvedReferences
        devices = self.get_switches().output.values()
        return [
            {
                'name': '{} - {}'.format(self._nodes_cache['by_id'][dev['node_id']]['name'],
                                         dev.get('label', '[No Label]')),
                'on': dev['data'],
                'id': dev['value_id'],
            } for dev in devices
        ]


# vim:sw=4:ts=4:et:
