from typing import Any, Dict, Optional, List, Union

from platypush.backend.zwave import ZwaveBackend
from platypush.context import get_backend
from platypush.plugins import action
from platypush.plugins.zwave._base import ZwaveBasePlugin


class ZwavePlugin(ZwaveBasePlugin):
    """
    This plugin interacts with the devices on a Z-Wave network started through the
    :class:`platypush.backend.zwave.ZwaveBackend` backend.

    .. note::

        This plugin is deprecated, since the underlying ``python-openzwave`` is
        quite buggy and largely unmaintained.

        Use the `zwave.mqtt` plugin instead
        (:class:`platypush.plugins.zwave.mqtt.ZwaveMqttPlugin`).

    Requires:

        * **python-openzwave** (``pip install python-openzwave``)
        * The :class:`platypush.backend.zwave.ZwaveBackend` backend configured and running.

    """

    @staticmethod
    def _get_backend() -> ZwaveBackend:
        backend = get_backend('zwave')
        if not backend:
            raise AssertionError('Z-Wave backend not configured')

        return backend

    @classmethod
    def _get_network(cls):
        backend = cls._get_backend()
        if not backend.network:
            backend.start_network()

        assert backend.network
        return backend.network

    @classmethod
    def _get_controller(cls):
        return cls._get_network().controller

    @action
    def start_network(self):
        backend = self._get_backend()
        backend.start_network()

    @action
    def stop_network(self):
        backend = self._get_backend()
        backend.stop_network()

    @action
    def status(self) -> Dict[str, Any]:
        """
        Get the status of the controller.

        :return: dict
        """
        backend = self._get_backend()
        network = self._get_network()
        controller = self._get_controller()

        return {
            'device': backend.device,
            'state': network.state_str,
            'stats': controller.stats,
        }

    @action
    def add_node(self, do_security=False, **_):
        """
        Start the inclusion process to add a node to the network.

        :param do_security: Whether to initialize the Network Key on the device if it supports the Security CC
        """
        controller = self._get_controller()
        controller.add_node(do_security)

    @action
    def remove_node(self, **_):
        """
        Remove a node from the network.
        """
        controller = self._get_controller()
        controller.remove_node()
        self.write_config()

    @action
    def remove_failed_node(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Remove a failed node from the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        controller = self._get_controller()
        node = self._get_node(node_id=node_id, node_name=node_name)
        controller.remove_failed_node(node.node_id)
        self.write_config()

    @action
    def replace_failed_node(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Replace a failed node on the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        controller = self._get_controller()
        node = self._get_node(node_id=node_id, node_name=node_name)
        controller.replace_failed_node(node.node_id)
        self.write_config()

    @action
    def replication_send(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Send node information from the primary to the secondary controller.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        controller = self._get_controller()
        node = self._get_node(node_id=node_id, node_name=node_name)
        controller.replication_send(node.node_id)

    @action
    def request_network_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Request a network update to a node.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        controller = self._get_controller()
        node = self._get_node(node_id=node_id, node_name=node_name)
        controller.request_network_update(node.node_id)

    @action
    def request_node_neighbour_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Request a neighbours list update to a node.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        controller = self._get_controller()
        node = self._get_node(node_id=node_id, node_name=node_name)
        controller.request_node_neighbor_update(node.node_id)

    @staticmethod
    def value_to_dict(value) -> Dict[str, Any]:
        if not value:
            return {}

        return {
            'command_class': value.node.get_command_class_as_string(value.command_class)
            if value.command_class
            else None,
            'data': value.data,
            'data_as_string': value.data_as_string,
            'data_items': list(value.data_items)
            if isinstance(value.data_items, set)
            else value.data_items,
            'genre': value.genre,
            'help': value.help,
            'home_id': value.home_id,
            'id_on_network': value.id_on_network
            if value.parent_id is not None
            and value.command_class is not None
            and value.instance is not None
            and value.index is not None
            else None,
            'index': value.index,
            'instance': value.instance,
            'is_polled': value.is_polled,
            'is_read_only': value.is_read_only,
            'is_set': value.is_set,
            'is_write_only': value.is_write_only,
            'label': value.label,
            'last_update': value.last_update,
            'min': value.min,
            'max': value.max,
            'object_id': value.object_id,
            'outdated': value.outdated,
            'parent_id': value.parent_id,
            'poll_intensity': value.poll_intensity,
            'precision': value.precision,
            'type': value.type,
            'units': value.units,
            'use_cache': value.use_cache,
            'value_id': value.value_id,
        }

    @staticmethod
    def group_to_dict(group) -> Dict[str, Any]:
        if not group:
            return {}

        return {
            'index': group.index,
            'label': group.label,
            'max_associations': group.max_associations,
            'associations': group.associations,
        }

    @classmethod
    def node_to_dict(cls, node) -> Dict[str, Any]:
        if not node:
            return {}

        # noinspection PyProtectedMember
        return {
            'node_id': node.node_id,
            'home_id': node.home_id,
            'capabilities': list(node.capabilities),
            'command_classes': [
                node.get_command_class_as_string(cc)
                for cc in node.command_classes
                if cc
            ]
            if hasattr(node, 'command_classes')
            else [],
            'device_type': node.device_type if hasattr(node, 'device_type') else '',
            'groups': {
                group_id: cls.group_to_dict(group)
                for group_id, group in node.groups.items()
            },
            'is_awake': node.is_awake if hasattr(node, 'is_awake') else False,
            'is_failed': node.is_failed if hasattr(node, 'is_failed') else False,
            'is_beaming_device': node.is_beaming_device
            if hasattr(node, 'is_beaming_device')
            else False,
            'is_frequent_listening_device': node.is_frequent_listening_device
            if hasattr(node, 'is_frequent_listening_device')
            else False,
            'is_info_received': node.is_info_received
            if hasattr(node, 'is_info_received')
            else False,
            'is_listening_device': node.is_listening_device
            if hasattr(node, 'is_listening_device')
            else False,
            'is_locked': node.is_locked if hasattr(node, 'is_locked') else False,
            'is_ready': node.is_ready if hasattr(node, 'is_ready') else False,
            'is_routing_device': node.is_routing_device
            if hasattr(node, 'is_routing_device')
            else False,
            'is_security_device': node.is_security_device
            if hasattr(node, 'is_security_device')
            else False,
            'is_sleeping': node.is_sleeping if hasattr(node, 'is_sleeping') else False,
            'last_update': node.last_update if hasattr(node, 'last_update') else None,
            'location': node.location if hasattr(node, 'location') else None,
            'manufacturer_id': node.manufacturer_id
            if hasattr(node, 'manufacturer_id')
            else None,
            'manufacturer_name': node.manufacturer_name
            if hasattr(node, 'manufacturer_name')
            else None,
            'max_baud_rate': node.max_baud_rate
            if hasattr(node, 'max_baud_rate')
            else None,
            'neighbours': list(node.neighbors or [])
            if hasattr(node, 'neighbours')
            else [],
            'name': node.name if hasattr(node, 'name') else None,
            'outdated': node.outdated if hasattr(node, 'outdated') else False,
            'product_id': node.product_id if hasattr(node, 'product_id') else None,
            'product_name': node.product_name
            if hasattr(node, 'product_name')
            else None,
            'product_type': node.product_type
            if hasattr(node, 'product_type')
            else None,
            'query_stage': node.query_stage if hasattr(node, 'query_stage') else None,
            'role': node.role if hasattr(node, 'role') else None,
            'security': node.security if hasattr(node, 'security') else None,
            'specific': node.specific if hasattr(node, 'specific') else None,
            'type': node.type if hasattr(node, 'type') else None,
            'use_cache': node.use_cache if hasattr(node, 'use_cache') else False,
            'version': node.version if hasattr(node, 'version') else None,
            'values': {
                value.id_on_network: cls.value_to_dict(value)
                for _, value in (node.values or {}).items()
                if value.index is not None
                and value.instance is not None
                and value.command_class
                and value.parent_id is not None
                and value._network
                and value._network.home_id is not None
            }
            if hasattr(node, 'values')
            else {},
        }

    def _get_node(self, node_id: Optional[int] = None, node_name: Optional[str] = None):
        assert (
            node_id is not None or node_name is not None
        ), 'Specify either node_id or name'
        nodes = self._get_network().nodes

        if node_id is not None:
            assert node_id in nodes, 'No such node_id: {}'.format(node_id)
            return nodes[node_id]

        nodes = [n for n in nodes.values() if n.name == node_name]
        assert nodes, 'No such node name: {}'.format(node_name)
        return nodes[0]

    def _get_groups(self) -> dict:
        return {
            group_index: group
            for node in self._get_network().nodes.values()
            for group_index, group in node.groups.items()
        }

    def _get_group(
        self, group_index: Optional[int] = None, group_label: Optional[str] = None
    ):
        assert (
            group_index is not None or group_label is not None
        ), 'Specify either group_index or label'
        groups = self._get_groups()

        if group_index is not None:
            assert group_index in groups, 'No such group_index: {}'.format(group_index)
            return groups[group_index]

        groups = [g for g in groups.values() if g.label == group_label]
        assert groups, 'No such group label: {}'.format(group_label)
        return groups[0]

    def _get_scene(
        self, scene_id: Optional[int] = None, scene_label: Optional[str] = None
    ):
        assert (
            scene_id is not None or scene_label is not None
        ), 'Specify either scene_id or label'
        scenes = self._get_network().get_scenes()

        if scene_id is not None:
            assert scene_id in scenes, 'No such scene_id: {}'.format(scene_id)
            return scenes[scene_id]

        scenes = [s for s in scenes.values() if s['label'] == scene_label]
        assert scenes, 'No such scene label: {}'.format(scene_label)
        return scenes[0]

    @action
    def get_nodes(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the nodes associated to the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        if node_id is not None or node_name is not None:
            return self.node_to_dict(
                self._get_node(node_id=node_id, node_name=node_name)
            )

        return {
            node_id: self.node_to_dict(node)
            for node_id, node in self._get_network().nodes.items()
        }

    @action
    def get_node_stats(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the statistics of a node on the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        return node.stats

    @action
    def set_node_name(
        self,
        new_name: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Rename a node on the network.

        :param new_name: New name for the node.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.name = new_name
        self.write_config()

    @action
    def set_node_product_name(
        self,
        product_name: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Set the product name of a node.

        :param product_name: Product name.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.product_name = product_name
        self.write_config()

    @action
    def set_node_manufacturer_name(
        self,
        manufacturer_name: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Set the manufacturer name of a node.

        :param manufacturer_name: Manufacturer name.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.manufacturer_name = manufacturer_name
        self.write_config()

    @action
    def set_node_location(
        self,
        location: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Set the location of a node.

        :param location: Node location.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.location = location
        self.write_config()

    @action
    def cancel_command(self):
        """
        Cancel the current running command.
        """
        self._get_controller().cancel_command()

    @action
    def kill_command(self):
        """
        Immediately terminate any running command on the controller and release the lock.
        """
        self._get_controller().kill_command()

    @action
    def set_controller_name(self, name: str):
        """
        Set the name of the controller on the network.

        :param name: New controller name.
        """
        self._get_controller().name = name
        self.write_config()

    @action
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of the controller.
        """
        return list(self._get_controller().capabilities)

    @action
    def receive_configuration(self):
        """
        Receive the configuration from the primary controller on the network. Requires a primary controller active.
        """
        self._get_controller().receive_configuration()

    @action
    def transfer_primary_role(self):
        """
        Add a new controller to the network and make it the primary.
        The existing primary will become a secondary controller.
        """
        self._get_controller().transfer_primary_role()

    @action
    def heal(self, refresh_routes: bool = False):
        """
        Heal network by requesting nodes rediscover their neighbors.

        :param refresh_routes: Whether to perform return routes initialization (default: ``False``).
        """
        self._get_network().heal(refresh_routes)

    @action
    def switch_all(self, state: bool):
        """
        Switch all the connected devices on/off.

        :param state: True (switch on) or False (switch off).
        """
        self._get_network().switch_all(state)

    @action
    def test(self, count: int = 1):
        """
        Send a number of test messages to every node and record results.

        :param count: The number of test messages to send.
        """
        self._get_network().test(count)

    def _get_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        value_label: Optional[str] = None,
    ):
        assert (value_id is not None or id_on_network is not None) or (
            (node_id is not None or node_name is not None) and value_label is not None
        ), 'Specify either value_id, id_on_network, or [node_id/node_name, value_label]'

        if value_id is not None:
            return self._get_network().get_value(value_id)
        if id_on_network is not None:
            values = [
                value
                for node in self._get_network().nodes.values()
                for value in node.values.values()
                if value.id_on_network == id_on_network
            ]

            assert values, 'No such value ID: {}'.format(id_on_network)
            return values[0]

        node = self._get_node(node_id=node_id, node_name=node_name)
        values = [v for v in node.values.values() if v.label == value_label]
        assert values, 'No such value on node "{}": "{}"'.format(node.name, value_label)
        return values[0]

    @action
    def get_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a value on the network.

        :param value_id: Select by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        """
        return self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            value_label=value_label,
        ).to_dict()

    @action
    def set_value(
        self,
        data,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Set a value.

        :param data: Data to set for the value.
        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        """
        from openzwave.node import ZWaveNode

        value = self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            value_label=value_label,
        )
        new_val = value.check_data(data)
        assert new_val is not None, 'Invalid value passed to the property'
        node: ZWaveNode = self._get_network().nodes[value.node.node_id]
        node.values[value.value_id].data = new_val
        self.write_config()

    @action
    def set_value_label(
        self,
        new_label: str,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Change the label/name of a value.

        :param new_label: New value label.
        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        """
        value = self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            value_label=value_label,
        )
        value.label = new_label
        self.write_config()

    @action
    def node_add_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Add a value to a node.

        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by label.
        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        value = self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            node_id=node.node_id,
            value_label=value_label,
        )
        node.add_value(value.value_id)
        self.write_config()

    @action
    def node_remove_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Remove a value from a node.

        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        value = self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            node_id=node.node_id,
            value_label=value_label,
        )
        node.remove_value(value.value_id)
        self.write_config()

    @action
    def node_heal(
        self,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        refresh_routes: bool = False,
    ):
        """
        Heal network node by requesting the node to rediscover their neighbours.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param refresh_routes: Whether to perform return routes initialization. (default: ``False``).
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.heal(refresh_routes)

    @action
    def node_update_neighbours(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Ask a node to update its neighbours table.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.neighbor_update()

    @action
    def node_network_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Update the controller with network information.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.network_update()

    @action
    def node_refresh_info(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ):
        """
        Fetch up-to-date information about the node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        node.refresh_info()

    def _get_values(
        self, item: str, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        nodes = (
            [self._get_node(node_id=node_id, node_name=node_name)]
            if node_id or node_name
            else self._get_network().nodes.values()
        )

        return {
            value.id_on_network: {
                'node_id': node.node_id,
                'node_name': node.name,
                **self.value_to_dict(value),
            }
            for node in nodes
            for value in getattr(node, 'get_' + item)().values()
        }

    @action
    def get_dimmers(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the dimmers on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        return self._get_values('dimmers', node_id=node_id, node_name=node_name)

    @action
    def get_node_config(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the configuration values of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        return self._get_values('configs', node_id=node_id, node_name=node_name)

    @action
    def get_battery_levels(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the battery levels of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('battery_levels', node_id=node_id, node_name=node_name)

    @action
    def get_power_levels(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the power levels of this node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('power_levels', node_id=node_id, node_name=node_name)

    @action
    def get_bulbs(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the bulbs/LEDs on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('rgbbulbs', node_id=node_id, node_name=node_name)

    @action
    def get_switches(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the switches on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('switches', node_id=node_id, node_name=node_name)

    @action
    def get_sensors(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the sensors on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('sensors', node_id=node_id, node_name=node_name)

    @action
    def get_doorlocks(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the doorlocks on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('doorlocks', node_id=node_id, node_name=node_name)

    @action
    def get_usercodes(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the usercodes on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('usercodes', node_id=node_id, node_name=node_name)

    @action
    def get_thermostats(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the thermostats on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('thermostats', node_id=node_id, node_name=node_name)

    @action
    def get_protections(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None
    ) -> Dict[int, Any]:
        """
        Get the protection-compatible devices on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        return self._get_values('protections', node_id=node_id, node_name=node_name)

    @action
    def get_groups(self) -> Dict[int, Any]:
        """
        Get the groups on the network.
        """
        return {
            group_index: self.group_to_dict(group)
            for group_index, group in self._get_groups().items()
        }

    @action
    def get_scenes(self) -> Dict[str, Any]:
        """
        Get the scenes configured on the network.
        """
        network = self._get_network()
        if not network.get_scenes():
            return {}

        return network.scenes_to_dict()

    @action
    def create_scene(self, label: str):
        """
        Create a new scene.

        :param label: Scene label.
        """
        self._get_network().create_scene(label)
        self.write_config()

    @action
    def remove_scene(
        self, scene_id: Optional[int] = None, scene_label: Optional[str] = None
    ):
        """
        Remove a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label)
        self._get_network().remove_scene(scene.scene_id)
        self.write_config()

    @action
    def activate_scene(
        self, scene_id: Optional[int] = None, scene_label: Optional[str] = None
    ):
        """
        Activate a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label)
        scene.activate()

    @action
    def set_scene_label(
        self,
        new_label: str,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
    ):
        """
        Rename a scene/set the scene label.

        :param new_label: New label.
        :param scene_id: Select by scene_id.
        :param scene_label: Select by current scene label.
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label)
        scene.label = new_label
        self.write_config()

    @action
    def scene_add_value(
        self,
        data: Optional[Any] = None,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Add a value to a scene.

        WARNING: This method actually doesn't work, by own admission of the
        `OpenZWave developer
        <https://github.com/OpenZWave/python-openzwave/blob/master/src-lib/libopenzwave/libopenzwave.pyx#L4730>`_.


        :param data: Data to set for the value (default: current value data).
        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        :param scene_id: Select scene by scene_id.
        :param scene_label: Select scene by scene label.
        """
        value = self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            value_label=value_label,
        )
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label)
        data = data if data is not None else value.data
        data = value.check_data(data)
        assert data is not None, 'Invalid value passed to the property'

        scene.add_value(value.value_id, data)
        self.write_config()

    @action
    def scene_remove_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
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
        """
        value = self._get_value(
            value_id=value_id,
            id_on_network=id_on_network,
            node_id=node_id,
            node_name=node_name,
            value_label=value_label,
        )
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label)
        scene.remove_value(value.value_id)
        self.write_config()

    @action
    def get_scene_values(
        self, scene_id: Optional[int] = None, scene_label: Optional[str] = None
    ) -> dict:
        """
        Get the values associated to a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        :return: value_id -> value (as a dict) mapping.
        """
        scene = self._get_scene(scene_id=scene_id, scene_label=scene_label)
        return {v.value_id: v.to_dict() for v in scene.get_values().items()}

    @action
    def create_button(
        self,
        button_id: Union[int, str],
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Create a handheld button on a device. Only intended for bridge firmware controllers.

        :param button_id: The ID of the button.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        self._get_controller().create_button(node.node_id, button_id)
        self.write_config()

    @action
    def delete_button(
        self,
        button_id: Union[int, str],
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Delete a button association from a device. Only intended for bridge firmware controllers.

        :param button_id: The ID of the button.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        self._get_controller().delete_button(node.node_id, button_id)
        self.write_config()

    @action
    def add_node_to_group(
        self,
        group_index: Optional[int] = None,
        group_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Add a node to a group.

        :param group_index: Select group by group index.
        :param group_label: Select group by group label.
        :param node_id: Select node by node_id.
        :param node_name: Select node by node name.
        :return:
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        group = self._get_group(group_index=group_index, group_label=group_label)
        group.add_association(node.node_id)
        self.write_config()

    @action
    def remove_node_from_group(
        self,
        group_index: Optional[int] = None,
        group_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
    ):
        """
        Remove a node from a group.

        :param group_index: Select group by group index.
        :param group_label: Select group by group label.
        :param node_id: Select node by node_id.
        :param node_name: Select node by node name.
        :return:
        """
        node = self._get_node(node_id=node_id, node_name=node_name)
        group = self._get_group(group_index=group_index, group_label=group_label)
        group.remove_association(node.node_id)
        self.write_config()

    @action
    def create_new_primary(self):
        """
        Create a new primary controller on the network when the previous primary fails.
        """
        self._get_controller().create_new_primary()
        self.write_config()

    @action
    def hard_reset(self):
        """
        Perform a hard reset of the controller. It erases its network configuration settings.
        The controller becomes a primary controller ready to add devices to a new network.
        """
        self._get_controller().hard_reset()

    @action
    def soft_reset(self):
        """
        Perform a soft reset of the controller.
        Resets a controller without erasing its network configuration settings.
        """
        self._get_controller().soft_reset()

    @action
    def write_config(self):
        """
        Store the current configuration of the network to the user directory.
        """
        self._get_network().write_config()

    @action
    def on(self, device: str, *_, **__):
        """
        Turn on a switch on a device.

        :param device: ``id_on_network`` of the value to be switched on.
        """
        # noinspection PyUnresolvedReferences
        switches = self.get_switches().output
        assert (
            device in switches
        ), 'No such id_on_network associated to a switch: {}'.format(device)
        return self.set_value(data=True, id_on_network=device)

    @action
    def off(self, device: str, *_, **__):
        """
        Turn off a switch on a device.

        :param device: ``id_on_network`` of the value to be switched off.
        """
        # noinspection PyUnresolvedReferences
        switches = self.get_switches().output
        assert (
            device in switches
        ), 'No such id_on_network associated to a switch: {}'.format(device)
        return self.set_value(data=False, id_on_network=device)

    @action
    def toggle(self, device: str, *_, **__):
        """
        Toggle a switch on a device.

        :param device: ``id_on_network`` of the value to be toggled.
        """
        # noinspection PyUnresolvedReferences
        switches = self.get_switches().output
        assert (
            device in switches
        ), 'No such id_on_network associated to a switch: {}'.format(device)
        data = switches[device]['data']
        return self.set_value(data=not data, id_on_network=device)

    @property
    def switches(self) -> List[dict]:
        # noinspection PyUnresolvedReferences
        devices = self.get_switches().output.values()
        return [
            {
                'name': '{} - {}'.format(
                    dev.get('node_name', '[No Name]'), dev.get('label', '[No Label]')
                ),
                'on': dev.get('data'),
                'id': dev.get('id_on_network'),
            }
            for dev in devices
        ]


# vim:sw=4:ts=4:et:
