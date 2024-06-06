import contextlib
import json
import queue
import re

from collections import OrderedDict
from datetime import datetime
from threading import Timer
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)
from urllib.parse import parse_qs, urlparse

from platypush.entities import (
    DimmerEntityManager,
    EnumSwitchEntityManager,
    Entity,
    LightEntityManager,
    SensorEntityManager,
    SwitchEntityManager,
)
from platypush.entities.batteries import Battery
from platypush.entities.devices import Device
from platypush.entities.dimmers import Dimmer
from platypush.entities.electricity import (
    EnergySensor,
    PowerSensor,
    VoltageSensor,
)
from platypush.entities.humidity import HumiditySensor
from platypush.entities.illuminance import IlluminanceSensor
from platypush.entities.lights import Light
from platypush.entities.sensors import BinarySensor, EnumSensor, NumericSensor
from platypush.entities.switches import EnumSwitch, Switch
from platypush.entities.temperature import TemperatureSensor
from platypush.message.event.zwave import (
    ZwaveEvent,
    ZwaveNodeAddedEvent,
    ZwaveNodeAsleepEvent,
    ZwaveNodeAwakeEvent,
    ZwaveNodeEvent,
    ZwaveNodeReadyEvent,
    ZwaveNodeRemovedEvent,
    ZwaveNodeRenamedEvent,
    ZwaveValueChangedEvent,
    ZwaveValueRemovedEvent,
)

from platypush.context import get_bus
from platypush.message.response import Response
from platypush.plugins import RunnablePlugin
from platypush.plugins.mqtt import MqttPlugin, action
from platypush.plugins.zwave._constants import command_class_by_name

from ._state import IdType, State


# pylint: disable=too-many-ancestors
class ZwaveMqttPlugin(
    MqttPlugin,
    RunnablePlugin,
    DimmerEntityManager,
    EnumSwitchEntityManager,
    LightEntityManager,
    SensorEntityManager,
    SwitchEntityManager,
):
    """
    This plugin allows you to manage a Z-Wave network over MQTT through
    `zwave-js-ui <https://github.com/zwave-js/zwave-js-ui>`_.

    Configuration required on the zwave-js-ui gateway:

        * Install the gateway following the instructions reported
          `here <https://zwave-js.github.io/zwave-js-ui/#/getting-started/quick-start>`_.

        * Configure the following settings from the zwave-js-ui web panel:

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

    """

    # These classes are ignored by the entity parsing logic
    _ignored_entity_classes = {
        'application_status',
        'association_command_configuration',
        'controller_replication',
        'crc16_encap',
        'firmware_update_md',
        'grouping_name',
        'ip_configuration',
        'manufacturer_proprietary',
        'manufacturer_specific',
        'multi_cmd',
        'multi_instance',
        'multi_instance_association',
        'no_operation',
        'node_naming',
        'non_interoperable',
        'proprietary',
        'scene_actuator_conf',
        'scene_controller_conf',
        'sensor_configuration',
        'version',
        'wake_up',
        'zwave_plus_info',
    }

    def __init__(
        self,
        name: str,
        host: str,
        port: int = 1883,
        topic_prefix: str = 'zwave',
        timeout: int = 10,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version: Optional[str] = None,
        tls_ciphers: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ):
        """
        :param name: Gateway name, as configured from the zwavejs2mqtt web
            panel from Mqtt -> Name.
        :param host: MQTT broker host, as configured from the zwavejs2mqtt web
            panel from Mqtt -> Host
        :param port: MQTT broker listen port, as configured from the
            zwavejs2mqtt web panel from Mqtt -> Port (default: 1883).
        :param topic_prefix: MQTT topic prefix, as specified from the
            zwavejs2mqtt web panel from Mqtt -> Prefix (default: ``zwave``).
        :param timeout: If the command expects from a response, then this
            timeout value will be used (default: 10 seconds).
        :param tls_cafile: If the connection requires TLS/SSL, specify the
            certificate authority file (default: None)
        :param tls_certfile: If the connection requires TLS/SSL, specify the
            certificate file (default: None)
        :param tls_keyfile: If the connection requires TLS/SSL, specify the key
            file (default: None)
        :param tls_version: If the connection requires TLS/SSL, specify the
            minimum TLS supported version (default: None)
        :param tls_ciphers: If the connection requires TLS/SSL, specify the
            supported ciphers (default: None)
        :param username: If the connection requires user authentication,
            specify the username (default: None)
        :param password: If the connection requires user authentication,
            specify the password (default: None)
        """

        self.topic_prefix = topic_prefix
        self.base_topic = topic_prefix + '/{}/ZWAVE_GATEWAY-' + name
        self.events_topic = self.base_topic.format('_EVENTS')
        super().__init__(
            host=host,
            port=port,
            topics=[
                self.events_topic + '/node/' + topic
                for topic in [
                    'node_ready',
                    'node_sleep',
                    'node_value_updated',
                    'node_metadata_updated',
                    'node_wakeup',
                ]
            ],
            tls_certfile=tls_certfile,
            tls_keyfile=tls_keyfile,
            tls_version=tls_version,
            tls_ciphers=tls_ciphers,
            username=username,
            password=password,
            timeout=timeout,
            **kwargs,
        )

        self._state = State()

    def _api_topic(self, api: str) -> str:
        return self.base_topic.format('_CLIENTS') + f'/api/{api}'

    @staticmethod
    def _parse_response(response: Union[dict, Response]) -> dict:
        if isinstance(response, Response):
            assert not response.is_error(), response.errors[0]

        rs: dict = (
            response.output if isinstance(response, Response) else response
        )  # type: ignore

        assert rs.get('success') is True, rs.get('message', 'zwavejs2mqtt error')
        return rs

    def _api_request(self, api: str, *args: Any, **kwargs):
        if len(args) == 1 and isinstance(args[0], dict):
            args = args[0]  # type: ignore

        payload = json.dumps({'args': args})
        ret = self._parse_response(
            self.publish(
                topic=self._api_topic(api) + '/set',
                msg=payload,
                reply_topic=self._api_topic(api),
                **self._mqtt_args(**kwargs),
            )
        )

        assert not ret or ret.get('success') is True, ret.get('message')
        return ret.get('result')

    @staticmethod
    def _convert_timestamp(t: Optional[int]) -> Optional[datetime]:
        if t:
            return datetime.fromtimestamp(t / 1000)
        return None

    def _get_scene(
        self,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs,
    ) -> dict:
        assert not (
            scene_id is None and scene_label is None
        ), 'No scene_id/scene_label specified'

        scene = self._state.scenes.get((scene_id, scene_label))
        if scene:
            return scene

        self._refresh_scenes(**kwargs)
        scene = self._state.scenes.get((scene_id, scene_label))
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
        if value.get('list'):
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
        is_read_only = (
            value['is_read_only']
            if 'is_read_only' in value
            else value.get('readable') and not value.get('writeable')
        )

        is_write_only = (
            value['is_write_only']
            if 'is_write_only' in value
            else not value.get('readable') and value.get('writeable')
        )

        return {
            'id': value['id'],
            'id_on_network': value['id'],
            'value_id': value['id'],
            'data': value.get('value'),
            'data_items': value['states'] if len(value.get('states', [])) > 1 else None,
            'label': value.get(
                'label', value.get('propertyName', value.get('property'))
            ),
            'property_id': value.get('property'),
            'help': value.get('description', value.get('help')),
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
            'is_read_only': is_read_only,
            'is_write_only': is_write_only,
            'last_update': cls._convert_timestamp(value.get('lastUpdate')),
            **(
                {'property_key': value['propertyKey']} if 'propertyKey' in value else {}
            ),
            **(
                {'property_key_name': value['propertyKeyName']}
                if 'propertyKeyName' in value
                else {}
            ),
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
        if node.get('supportsBeaming'):
            capabilities += ['beaming']
        if node.get('supportsSecurity'):
            capabilities += ['security']
        if node.get('isRouting'):
            capabilities += ['routing']
        if node.get('zwavePlusVersion'):
            capabilities += ['zwave_plus']

        db_link = node.get('dbLink', node.get('db_link', ''))
        device_id = node.get('hexId')
        if not device_id:
            if db_link:
                # noinspection PyTypeChecker
                device_id = ':'.join(
                    parse_qs(urlparse(db_link).query)
                    .get('jumpTo', '')[0]
                    .split(':')[:-1]
                )
            else:
                device_id = str(node['id'])

        return {
            'node_id': node['id'],
            'device_id': device_id.replace('0x', ''),
            'name': node.get('name'),
            'capabilities': capabilities,
            'manufacturer_id': (
                f'0x{node["manufacturerId"]:04x}'
                if node.get('manufacturerId')
                else None
            ),
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
            'product_id': (
                f'0x{node["productId"]:04x}' if node.get('productId') else None
            ),
            'product_type': (
                f'0x{node["productType"]:04x}' if node.get('productType') else None
            ),
            'product_name': ' '.join(
                [node.get('productLabel', ''), node.get('productDescription', '')]
            ),
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
                for value in node.get('values', {}).values()
                if value.get('commandClassName')
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

    def _refresh_groups(self, **kwargs):
        nodes = self._get_nodes(**kwargs)
        groups = {
            group['group_id']: {
                **group,
                'associations': [
                    assoc['nodeId']
                    for assoc in (
                        self._api_request('getAssociations', node_id, group['index'])
                        or []
                    )
                ],
            }
            for node_id, node in nodes.items()
            for group in node.get('groups', {}).values()
        }

        self._state.groups.add(*groups.values(), overwrite=True)

    def _get_groups(self, **kwargs) -> Dict[IdType, dict]:
        self._refresh_groups(**kwargs)
        return self._state.groups.by_id

    def _refresh_scenes(self, **kwargs):
        scenes = {
            scene.get('sceneid'): self.scene_to_dict(scene)
            for scene in (self._api_request('_getScenes', **kwargs) or [])
        }

        self._state.scenes.add(*scenes.values(), overwrite=True)

    def _get_scenes(self, **kwargs) -> Dict[IdType, dict]:
        self._refresh_scenes(**kwargs)
        return self._state.scenes.by_id

    def _refresh_nodes(self, **kwargs):
        nodes = {
            node['id']: {'id': node['id'], **self.node_to_dict(node)}
            for node in (self._api_request('getNodes', **kwargs) or [])
        }

        values = [
            value
            for node in nodes.values()
            for value in node.get('values', {}).values()
        ]

        # Process events for the newly received nodes
        for node_id, node in nodes.items():
            if node_id not in self._state.nodes:
                self._dispatch_event(ZwaveNodeAddedEvent, node=node, fetch_node=False)
            elif node['name'] != self._state.nodes.get('name'):
                self._dispatch_event(ZwaveNodeRenamedEvent, node=node, fetch_node=False)

        # Check if any previous node is now missing
        for node_id, node in self._state.nodes.by_id.items():
            if node_id not in nodes:
                self._dispatch_event(ZwaveNodeRemovedEvent, node=node, fetch_node=False)

        self._state.nodes.add(*nodes.values(), overwrite=True)
        self._state.values.add(*values, overwrite=True)
        self.publish_entities([self._to_current_value(v) for v in values])

    def _get_nodes(self, **kwargs) -> Dict[IdType, dict]:
        self._refresh_nodes(**kwargs)
        return self._state.nodes.by_id

    def _get_node(
        self,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        use_cache: bool = True,
        make_request: bool = True,
        **kwargs,
    ) -> dict:
        assert node_id or node_name, 'Please provide either a node_id or node_name'
        if use_cache:
            node = self._state.nodes.get((node_id, node_name))
            if node:
                return node

        assert make_request, f'No such node: {node_id or node_name}'
        self._refresh_nodes(**kwargs)
        return self._get_node(
            node_id=node_id,
            node_name=node_name,
            use_cache=True,
            make_request=False,
            **kwargs,
        )

    def _get_value(
        self,
        value_id: Optional[str] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        use_cache: bool = True,
        make_request: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        # Unlike python-openzwave, value_id and id_on_network are the same on zwavejs2mqtt
        value_id = value_id or id_on_network
        assert (
            value_id or value_label
        ), 'Please provide either value_id, id_on_network or value_label'

        if use_cache:
            value = self._state.values.get((value_id, value_label))
            if value:
                if node_id or node_name:
                    node = self._state.nodes.get((node_id, node_name))
                    assert node, f'No such node: {node_id or node_name}'
                    assert (
                        value['node_id'] == node['id']
                    ), f'No such value on node {node_id or node_name}: {value_id or value_label}'

                return value

        assert make_request, f'No such value: {value_id or value_label}'
        self._refresh_nodes(**kwargs)
        return self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            value_label=value_label,
            node_id=node_id,
            node_name=node_name,
            use_cache=True,
            make_request=False,
            **kwargs,
        )

    @staticmethod
    def _is_target_value(value: Mapping):
        return value.get('property_id') in {'targetValue', 'targetColor'}

    @staticmethod
    def _is_current_value(value: Mapping):
        return value.get('property_id') in {'currentValue', 'currentColor'}

    def _to_current_value(self, value: dict) -> dict:
        return self._get_associated_value(value, 'current')

    def _to_target_value(self, value: dict) -> dict:
        return self._get_associated_value(value, 'target')

    def _get_associated_value(self, value: dict, target: str) -> dict:
        check_func = (
            self._is_target_value if target == 'current' else self._is_current_value
        )

        if not check_func(value):
            return value

        replace_args = (
            ('target', 'current') if target == 'current' else ('current', 'target')
        )

        associated_value_id = '-'.join(
            value['value_id'].split('-')[:-1]
            + [value['value_id'].split('-')[-1].replace(*replace_args)]
        )

        associated_value = self._state.values.get(associated_value_id)
        if associated_value:
            value = associated_value

        return value.copy()

    @staticmethod
    def _matches_classes(value: Mapping, *names: str):
        classes = {command_class_by_name[name] for name in names}
        return value.get('command_class', '') in classes if value else False

    @classmethod
    def _is_switch(cls, value: Mapping):
        return value.get('type') == 'Bool' and not value.get('is_read_only')

    @classmethod
    def _is_dimmer(cls, value: Mapping):
        return value.get('type') == 'Decimal' and not value.get('is_read_only')

    @classmethod
    def _is_enum_switch(cls, value: Mapping):
        return value.get('type') == 'List' and not value.get('is_read_only')

    @classmethod
    def _is_light(cls, value: Mapping):
        return (
            cls._matches_classes(value, 'color')
            and not {'red', 'green', 'blue'}.difference(
                set(value.get('value', {}).keys())
            )
            and not value.get('is_read_only')
        )

    @classmethod
    def _is_configuration_value(cls, value: Mapping):
        return cls._matches_classes(value, 'configuration')

    @classmethod
    def _get_sensor_args(
        cls, value: Mapping
    ) -> Tuple[Optional[Type], Optional[Mapping]]:
        sensor_type, args = None, None

        if value.get('is_read_only'):
            if value.get('type') == 'Bool':
                sensor_type, args = (
                    BinarySensor,
                    {
                        'value': value.get('data', False),
                    },
                )
            elif value.get('type') == 'List':
                sensor_type, args = (
                    EnumSensor,
                    {
                        'value': value.get('data'),
                        'values': {
                            i['value']: i['text'] for i in value.get('data_items', [])
                        },
                    },
                )
            elif value.get('type') == 'Decimal':
                sensor_type = NumericSensor
                if re.search(r'\s*power$', value['property_id'], re.IGNORECASE):
                    sensor_type = PowerSensor
                if re.search(r'\s*voltage$', value['property_id'], re.IGNORECASE):
                    sensor_type = VoltageSensor
                elif re.search(
                    r'\s*consumption$', value['property_id'], re.IGNORECASE
                ) or re.search(r'Wh$', (value.get('units') or '')):
                    sensor_type = EnergySensor
                elif re.search(r'\s*temperature$', value['property_id'], re.IGNORECASE):
                    sensor_type = TemperatureSensor
                elif re.search(
                    r'\s*(humidity|moisture)$', value['property_id'], re.IGNORECASE
                ):
                    sensor_type = HumiditySensor
                elif re.search(
                    r'\s*(illuminance|luminosity)$', value['property_id'], re.IGNORECASE
                ):
                    sensor_type = IlluminanceSensor

                args = {
                    'value': value.get('data'),
                    'min': value.get('min'),
                    'max': value.get('max'),
                    'unit': value.get('units'),
                }

        return sensor_type, args

    @classmethod
    def _is_battery(cls, value: Mapping):
        return (
            cls._matches_classes(value, 'battery')
            and value.get('is_read_only')
            and value.get('type') == 'Decimal'
        )

    def _to_entity_args(self, value: dict) -> dict:
        value = self._to_current_value(value)
        args = {
            'id': value['id'],
            'name': value.get('label'),
            'description': value.get('help'),
            'is_read_only': value.get('is_read_only'),
            'is_write_only': value.get('is_write_only'),
            'is_configuration': self._is_configuration_value(value),
        }

        if value.get('last_update'):
            args['updated_at'] = value['last_update']
        return args

    def transform_entities(self, entities: Iterable[dict]) -> Collection[Entity]:
        transformed_entities = []

        for value in entities:
            if not value or self._matches_classes(value, *self._ignored_entity_classes):
                continue

            value = value.copy()
            current_value = target_value = None
            if self._is_current_value(value):
                current_value = value
                target_value = self._to_target_value(value)
            elif self._is_target_value(value):
                current_value = self._to_current_value(value)
                target_value = value

            if current_value and target_value:
                value = self._merge_current_and_target_values(
                    [current_value, target_value]
                )[0]

            entity_type = None
            entity_args = self._to_entity_args(value)
            sensor_type, sensor_args = self._get_sensor_args(value)

            if self._is_light(value):
                entity_type = Light
                color = value['value']
                entity_args['red'] = color['red']
                entity_args['green'] = color['green']
                entity_args['blue'] = color['blue']
            elif self._is_dimmer(value):
                entity_type = Dimmer
                entity_args['value'] = value['data']
                entity_args['min'] = value['min']
                entity_args['max'] = value['max']
            elif self._is_enum_switch(value):
                entity_type = EnumSwitch
                entity_args['value'] = value['data']
                entity_args['values'] = {
                    i['value']: i['text'] for i in value.get('data_items', [])
                }
            elif self._is_battery(value):
                entity_type = Battery
                entity_args['value'] = value['data']
                entity_args['min'] = value['min']
                entity_args['max'] = value['max']
                entity_args['unit'] = value.get('units', '%')
            elif self._is_switch(value):
                entity_type = Switch
                entity_args['state'] = value['data']
            elif sensor_args:
                entity_type = sensor_type
                entity_args.update(sensor_args)

            if entity_type:
                transformed_entities.append(entity_type(**entity_args))

        self._process_parent_entities(entities, transformed_entities)
        return transformed_entities

    def _process_parent_entities(
        self, values: Iterable[Mapping], entities: List[Entity]
    ):
        parent_entities: Dict[int, Device] = {}
        entities_by_id: Dict[str, Entity] = {str(e.id): e for e in entities}

        for value in values:
            if not (value and value.get('id')):
                continue

            entity = entities_by_id.get(value['id'])
            if not entity:
                continue

            parent_id = value.get('parent_id')
            if parent_id is None:
                continue

            node = self._state.nodes.get(parent_id)
            if not node:
                continue

            node_id = node['node_id']
            if node_id not in parent_entities:
                parent = parent_entities[node_id] = Device(
                    id=node['device_id'],
                    name=node.get('name'),
                    external_url=self._build_external_url(node),
                    reachable=(
                        node.get('is_available', False) and node.get('is_ready', False)
                    ),
                )
                entities.append(parent)

            parent = parent_entities[node_id]
            entity.parent = parent
            entity.reachable = parent.reachable

    @staticmethod
    def _build_external_url(node: dict) -> Optional[str]:
        manufacturer_id = node.get('manufacturer_id')
        product_id = node.get('product_id')
        product_type = node.get('product_type')
        firmware_version = node.get('firmware_version', '0.0')
        if not (manufacturer_id and product_id and product_type):
            return None

        return (
            'https://devices.zwave-js.io/?jumpTo='
            f'{manufacturer_id}:{product_type}:{product_id}:{firmware_version}'
        )

    @classmethod
    def _merge_current_and_target_values(cls, values: Iterable[dict]) -> List[dict]:
        values_by_id = OrderedDict({v.get('id'): v for v in values})

        new_values = OrderedDict()
        for value in values:
            value = value.copy()
            value_id = value.get('id')
            if not value_id:
                continue

            associated_value = None
            associated_property_id = None
            current_property_id = None
            current_value = None
            value_id_prefix = '-'.join(value_id.split('-')[:-1])

            if cls._is_current_value(value):
                associated_property_id = value['property_id'].replace(
                    'current', 'target'
                )
                current_property_id = value['property_id']
                current_value = value
            elif cls._is_target_value(value):
                associated_property_id = value['property_id'].replace(
                    'target', 'current'
                )
                current_property_id = associated_property_id

            if associated_property_id:
                associated_value_id = f'{value_id_prefix}-{associated_property_id}'
                associated_value = values_by_id.pop(associated_value_id, None)

                if cls._is_target_value(value):
                    current_value = associated_value

            if current_value and associated_value and current_property_id:
                value = value.copy()
                value_id = f'{value_id_prefix}-{current_property_id}'
                value['data'] = current_value.get('data')
                value['id'] = value['value_id'] = value['id_on_network'] = value_id
                value['is_read_only'] = value['is_write_only'] = False
                value['label'] = 'Value'
                value['property_id'] = current_property_id
                value['last_update'] = (
                    max(
                        value.get('last_update') or 0,
                        associated_value.get('last_update') or 0,
                    )
                    or None
                )

            new_values[value_id] = value

        return list(new_values.values())

    def _filter_values(
        self,
        command_classes: Optional[Iterable[str]] = None,
        filter_callback: Optional[Callable[[dict], bool]] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        nodes = (
            [self._get_node(node_name=node_name, use_cache=False, **kwargs)]
            if node_id or node_name
            else self._get_nodes(**kwargs).values()
        )

        classes: set = {
            command_class_by_name[command_name]
            for command_name in (command_classes or [])
        }

        values = {}

        for node in nodes:
            if not node:
                continue

            for value in node.get('values', {}).values():
                if (classes and value.get('command_class') not in classes) or (
                    filter_callback and not filter_callback(value)
                ):
                    continue

                value = self._to_current_value(value)
                values[value['id_on_network']] = value

        entity_values = self._merge_current_and_target_values(values.values())
        self.publish_entities(entity_values)  # type: ignore
        return values

    def _get_group(
        self,
        group_id: Optional[str] = None,
        group_index: Optional[int] = None,
        **kwargs,
    ) -> dict:
        assert not (
            group_id is None and group_index is None
        ), 'No group_id/group_index specified'
        group_id = group_id or str(group_index)
        group = self._state.groups.get(group_id)
        if group:
            return group

        groups = self._get_groups(**kwargs)
        assert group_id in groups, f'No such group_id: {group_id}'
        return groups[group_id]

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

    def _dispatch_event(
        self,
        event_type: Type[ZwaveEvent],
        node: dict,
        value: Optional[dict] = None,
        fetch_node: bool = True,
        **kwargs,
    ):
        node_id = node.get('id')
        assert node_id is not None, 'No node ID specified'

        if fetch_node:
            node = kwargs['node'] = self._get_node(node_id)
        else:
            kwargs['node'] = node

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

            if 'newValue' in value:
                node_values[value_id]['data'] = value['newValue']

            value = kwargs['value'] = node_values[value_id]

        if issubclass(event_type, ZwaveNodeEvent):
            # If this node_id wasn't cached before, then it's a new node
            if node_id not in self._state.nodes:
                event_type = ZwaveNodeAddedEvent
            # If the name has changed, we have a rename event
            elif node['name'] != (self._state.nodes.get(node_id) or {}).get('name'):
                event_type = ZwaveNodeRenamedEvent

        if event_type == ZwaveNodeRemovedEvent:
            # If the node has been removed, remove it from the cache
            self._state.nodes.pop(node_id, None)
        else:
            # Otherwise, update the cached instance
            self._state.nodes.add(node)
            values = node.get('values', {}).values()
            self._state.values.add(*values)

        evt = event_type(**kwargs)
        get_bus().post(evt)

        if (
            value
            and issubclass(event_type, ZwaveValueChangedEvent)
            and event_type != ZwaveValueRemovedEvent
        ):
            self.publish_entities([value])

    @action
    def status(self, *_, **kwargs) -> Dict[str, Any]:
        """
        Get the current status of the Z-Wave values.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(**kwargs)

    @action
    def controller_status(self, **kwargs) -> Dict[str, Any]:
        """
        Get the status of the controller.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        msg_queue: queue.Queue = queue.Queue()
        topic = f'{self.topic_prefix}/driver/status'
        client = self._get_client(**kwargs)

        def on_message(_, __, msg):
            if msg.topic != topic:
                return
            msg_queue.put(json.loads(msg.payload))

        client.on_message = on_message
        client.connect()
        client.subscribe(topic)
        client.loop_start()

        try:
            status = msg_queue.get(
                block=True, timeout=kwargs.get('timeout', self.timeout)
            )
        except queue.Empty as e:
            raise TimeoutError('The request timed out') from e
        finally:
            client.loop_stop()

        return {
            'state': status,
        }

    @action
    def add_node(  # pylint: disable=arguments-differ
        self,
        name: str,
        location: str = '',
        do_security: bool = False,
        timeout: int = 30,
        **kwargs,
    ):
        """
        Start the inclusion process to add a node to the network.

        :param name: Name of the node to be added.
        :param location: Location of the node (default: empty).
        :param do_security: Whether to initialize the Network Key on the device if it supports the Security CC
        :param timeout: How long the inclusion process should last, in seconds (default: 30). Specify zero or null
            for no timeout.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self._api_request(
            'startInclusion',
            0,
            {
                'name': name,
                'location': location,
                'force_security': do_security,
            },
            **kwargs,
        )

        if timeout:
            Timer(timeout, lambda: self._api_request('stopInclusion', **kwargs)).start()

    @action
    def remove_node(self, timeout: int = 30, **kwargs):
        """
        Remove a node from the network (or, better, start the exclusion process).

        :param timeout: How long the exclusion process should last, in seconds (default: 30).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self._api_request('startExclusion', **kwargs)
        if timeout:
            Timer(timeout, lambda: self._api_request('stopExclusion', **kwargs)).start()

    @action
    def remove_failed_node(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Remove a failed node from the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name).get('node_id')

        assert node_id is not None, f'No such node_id: {node_id}'
        self._api_request('removeFailedNode', node_id, **kwargs)

    @action
    def replace_failed_node(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Replace a failed node on the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name).get('node_id')

        assert node_id is not None, f'No such node_id: {node_id}'
        self._api_request('replaceFailedNode', node_id, **kwargs)

    @action
    def request_network_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Request a network update to a node.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name).get('node_id')

        assert node_id is not None, f'No such node_id: {node_id}'
        self._api_request('refreshInfo', node_id, **kwargs)

    @action
    def request_node_neighbour_update(self, *_, **kwargs):
        """
        Request a neighbours list update.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self._api_request('refreshNeighbors', **kwargs)

    @action
    def get_nodes(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Optional[Dict[IdType, dict]]:
        """
        Get the nodes associated to the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
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
                    "manufacturer_name": "FibaroGroup",
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

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_id or node_name:
            return self._get_node(
                node_id=node_id, node_name=node_name, use_cache=False, **kwargs
            )

        return self._get_nodes(**kwargs)

    @action
    def set_node_name(
        self,
        new_name: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Rename a node on the network.

        :param new_name: New name for the node.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')

        assert node_id, f'No such node: {node_id}'
        self._api_request('setNodeName', node_id, new_name, **kwargs)
        get_bus().post(
            ZwaveNodeRenamedEvent(
                node={
                    **self._get_node(node_id=node_id, **kwargs),
                    'name': new_name,
                }
            )
        )

    @action
    def set_node_location(
        self,
        location: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Set the location of a node.

        :param location: Node location.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')

        assert node_id, f'No such node: {node_id}'
        self._api_request('setNodeLocation', node_id, location, **kwargs)
        get_bus().post(
            ZwaveNodeEvent(
                node={
                    **self._get_node(node_id=node_id, **kwargs),
                    'location': location,
                }
            )
        )

    @action
    def heal(
        self, *_, timeout: Optional[int] = 60, **kwargs
    ):  # pylint: disable=arguments-differ
        """
        Heal network by requesting nodes rediscover their neighbours.

        :param timeout: Duration of the healing process in seconds (default: 60). Set to zero or null for no timeout.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self._api_request('beginHealingNetwork', **kwargs)
        if timeout:
            Timer(
                timeout, lambda: self._api_request('stopHealingNetwork', **kwargs)
            ).start()

    @action
    def get_value(
        self,
        value_id: Optional[str] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Get a value on the network.

        :param value_id: Select by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._get_value(
            value_id=value_id,
            value_label=value_label,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            use_cache=False,
            **kwargs,
        )

    @action
    def set_value(
        self,
        *args,
        data=None,
        value_id: Optional[str] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Set a value.

        :param data: Data to set for the value.
        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        # Compatibility layer with the .set_value format used by
        # the entities frontend
        if args:
            value_id = args[0]

        value = self._get_value(
            value_id=value_id,
            value_label=value_label,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )

        # Convert to target value if the value is in current value format,
        # as that would usually be the writeable attribute
        value = self._to_target_value(value)
        self._api_request(
            'writeValue',
            {
                'nodeId': value['node_id'],
                'commandClass': value['command_class'],
                'endpoint': value.get('endpoint', 0),
                'property': value['property_id'],
                **(
                    {'propertyKey': value['property_key']}
                    if 'property_key' in value
                    else {}
                ),
            },
            data,
            **kwargs,
        )

    @action
    def set_lights(self, lights, **kwargs):  # pylint: disable=arguments-differ
        """
        Set the state for one or more Z-Wave lights.
        """
        lights = [lights] if isinstance(lights, str) else lights
        for light in lights:
            self.set_value(light, kwargs)

    @action
    def node_heal(  # pylint: disable=arguments-differ
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Heal network node by requesting the node to rediscover their neighbours.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')
        self._api_request('healNode', node_id, **kwargs)

    @action
    def node_update_neighbours(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Ask a node to update its neighbours table
        (same as :meth:`platypush.plugins.zwave.mqtt.ZwaveMqttPlugin.node_heal`).

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self.node_heal(node_id=node_id, node_name=node_name, **kwargs)

    @action
    def node_network_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Update the controller with network information
        (same as :meth:`platypush.plugins.zwave.mqtt.ZwaveMqttPlugin.node_heal`).

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self.node_heal(node_id=node_id, node_name=node_name, **kwargs)

    @action
    def node_refresh_info(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Fetch up-to-date information about the node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        if node_name:
            node_id = self._get_node(node_name=node_name, **kwargs).get('node_id')
        self._api_request('refreshInfo', node_id, **kwargs)

    @action
    def get_dimmers(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the dimmers on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['switch_multilevel', 'switch_toggle_multilevel'],
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )

    @action
    def get_node_config(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the configuration values of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            [
                'configuration',
                'ip_configuration',
                'association_command_configuration',
                'sensor_configuration',
            ],
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )

    @action
    def get_battery_levels(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the battery levels of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['battery'], node_id=node_id, node_name=node_name, **kwargs
        )

    @action
    def get_power_levels(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the power levels of this node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['powerlevel'], node_id=node_id, node_name=node_name, **kwargs
        )

    @action
    def get_bulbs(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the bulbs/LEDs on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['color'],
            filter_callback=lambda value: not value['is_read_only'],
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )

    @action
    def get_switches(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the switches on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['switch_binary', 'switch_toggle_binary', 'switch_all'],
            filter_callback=lambda value: not value['is_read_only'],
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )

    @action
    def get_sensors(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the sensors on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['sensor_binary', 'sensor_multilevel', 'sensor_alarm', 'meter'],
            filter_callback=lambda value: not value['is_write_only'],
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )

    @action
    def get_doorlocks(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the doorlocks on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['door_lock'], node_id=node_id, node_name=node_name, **kwargs
        )

    @action
    def get_locks(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the locks on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['lock'], node_id=node_id, node_name=node_name, **kwargs
        )

    @action
    def get_usercodes(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the usercodes on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['user_code'], node_id=node_id, node_name=node_name, **kwargs
        )

    @action
    def get_thermostats(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the thermostats on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            [
                'thermostat_heating',
                'thermostat_mode',
                'thermostat_operating_state',
                'thermostat_setpoint',
                'thermostat_fan_mode',
                'thermostat_fan_state',
                'thermostat_setback',
            ],
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )

    @action
    def get_protections(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the protection-compatible devices on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        return self._filter_values(
            ['protection'], node_id=node_id, node_name=node_name, **kwargs
        )

    @action
    def get_groups(self, **kwargs) -> Dict[IdType, dict]:
        """
        Get the groups on the network.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
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
        return self._get_groups(**kwargs)

    @action
    def get_scenes(self, **kwargs) -> Dict[IdType, dict]:
        """
        Get the scenes configured on the network.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
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
        return self._get_scenes(**kwargs)

    @action
    def create_scene(self, label: str, **kwargs):
        """
        Create a new scene.

        :param label: Scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self._api_request('_createScene', label, **kwargs)

    @action
    def remove_scene(
        self,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs,
    ):
        """
        Remove a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        self._api_request('_removeScene', scene['scene_id'])

    @action
    def activate_scene(
        self,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs,
    ):
        """
        Activate a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        self._api_request('_activateScene', scene['scene_id'])

    @action
    def scene_add_value(
        self,
        data: Optional[Any] = None,
        value_id: Optional[str] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs,
    ):
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
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        value = self._get_value(
            value_id=value_id,
            value_label=value_label,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)

        self._api_request(
            '_addSceneValue',
            scene['scene_id'],
            {
                'nodeId': value['node_id'],
                'commandClass': value['command_class'],
                'property': value['property_id'],
                'endpoint': value['endpoint'],
            },
            data,
            kwargs.get('timeout', self.timeout),
        )

    @action
    def scene_remove_value(
        self,
        value_id: Optional[str] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Remove a value from a scene.

        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param scene_id: Select scene by scene_id.
        :param scene_label: Select scene by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        value = self._get_value(
            value_id=value_id,
            value_label=value_label,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            **kwargs,
        )
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        self._api_request('_removeSceneValue', scene['scene_id'], value['value_id'])

    @action
    def get_scene_values(
        self,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Get the values associated to a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label, **kwargs)
        return scene.get('values', {})

    @action
    def add_node_to_group(  # pylint: disable=arguments-differ
        self,
        group_id: Optional[str] = None,
        node_id: Optional[int] = None,
        endpoint: Optional[int] = None,
        **kwargs,
    ):
        """
        Add a node to a group.

        :param group_id: Group ID.
        :param node_id: Node ID to be added.
        :param endpoint: Add a specific endpoint of the node to the group (default: add a node association).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        group = self._get_group(group_id, **kwargs)
        assoc = {'nodeId': node_id}
        if endpoint is not None:
            assoc['endpoint'] = endpoint

        self._api_request('addAssociations', group['node_id'], group['index'], [assoc])

    @action
    def remove_node_from_group(  # pylint: disable=arguments-differ
        self,
        group_id: Optional[str] = None,
        node_id: Optional[int] = None,
        endpoint: Optional[int] = None,
        **kwargs,
    ):
        """
        Remove a node from a group.

        :param group_id: Group ID.
        :param node_id: Node ID to be added.
        :param endpoint: Node endpoint to remove (default: remove node association).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        group = self._get_group(group_id, **kwargs)
        assoc = {'nodeId': node_id}
        if endpoint is not None:
            assoc['endpoint'] = endpoint

        self._api_request(
            'removeAssociations', group['node_id'], group['index'], [assoc]
        )

    @action
    def hard_reset(self, **_):
        """
        Perform a hard reset of the controller. It erases its network configuration settings.
        The controller becomes a primary controller ready to add devices to a new network.
        """
        self._api_request('hardReset')

    @action
    def on(self, device: str, *_, **kwargs):  # pylint: disable=arguments-differ
        """
        Turn on a switch on a device.

        :param device: ``id_on_network`` of the value to be switched on.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self.set_value(data=True, id_on_network=device, **kwargs)

    @action
    def off(self, device: str, *_, **kwargs):  # pylint: disable=arguments-differ
        """
        Turn off a switch on a device.

        :param device: ``id_on_network`` of the value to be switched off.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        self.set_value(data=False, id_on_network=device, **kwargs)

    @action
    def toggle(  # pylint: disable=arguments-differ
        self, device: str, *_, **kwargs
    ) -> dict:
        """
        Toggle a switch on a device.

        :param device: ``id_on_network`` of the value to be toggled.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish`
            (default: query the default configured device).
        """
        value = self._get_value(id_on_network=device, use_cache=False, **kwargs)
        value['data'] = not value['data']
        self.set_value(data=value['data'], id_on_network=device, **kwargs)
        node = self._state.nodes.get(value['node_id'])
        assert node, f'Node {value["node_id"]} not found'

        return {
            'name': (node['name'] + ' - ' + value.get('label', '[No Label]')),
            'on': value['data'],
            'id': value['value_id'],
        }

    def main(self):
        self.get_nodes()
        super().main()


# vim:sw=4:ts=4:et:
