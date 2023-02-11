from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union

from platypush.entities import (
    DimmerEntityManager,
    EnumSwitchEntityManager,
    LightEntityManager,
    SensorEntityManager,
    SwitchEntityManager,
)
from platypush.plugins import Plugin, action


class ZwaveBasePlugin(
    DimmerEntityManager,
    EnumSwitchEntityManager,
    LightEntityManager,
    SensorEntityManager,
    SwitchEntityManager,
    Plugin,
    ABC,
):
    """
    Base class for Z-Wave plugins.
    """

    @abstractmethod
    @action
    def start_network(self):
        raise NotImplementedError

    @abstractmethod
    @action
    def stop_network(self):
        raise NotImplementedError

    @abstractmethod
    @action
    def status(self) -> Dict[str, Any]:  # pylint: disable=arguments-differ
        """
        Get the status of the controller.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def add_node(self, *args, **kwargs):
        """
        Start the inclusion process to add a node to the network.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def remove_node(self):
        """
        Remove a node from the network.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def remove_failed_node(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Remove a failed node from the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def replace_failed_node(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Replace a failed node on the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def replication_send(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Send node information from the primary to the secondary controller.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def request_network_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Request a network update to a node.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def request_node_neighbour_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Request a neighbours list update to a node.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_nodes(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the nodes associated to the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_node_stats(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the statistics of a node on the network.

        :param node_id: Filter by node_id.
        :param node_name: Filter by node name.
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    @action
    def set_node_product_name(
        self,
        product_name: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Set the product name of a node.

        :param product_name: Product name.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def set_node_manufacturer_name(
        self,
        manufacturer_name: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Set the manufacturer name of a node.

        :param manufacturer_name: Manufacturer name.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def set_node_location(
        self,
        location: str,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Set the location of a node.

        :param location: Node location.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def cancel_command(self):
        """
        Cancel the current running command.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def kill_command(self):
        """
        Immediately terminate any running command on the controller and release the lock.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def set_controller_name(self, name: str, **kwargs):
        """
        Set the name of the controller on the network.

        :param name: New controller name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_capabilities(self, **kwargs) -> List[str]:
        """
        Get the capabilities of the controller.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def receive_configuration(self, **kwargs):
        """
        Receive the configuration from the primary controller on the network. Requires a primary controller active.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def transfer_primary_role(self, **kwargs):
        """
        Add a new controller to the network and make it the primary.
        The existing primary will become a secondary controller.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def heal(self, refresh_routes: bool = False, **kwargs):
        """
        Heal network by requesting nodes rediscover their neighbors.

        :param refresh_routes: Whether to perform return routes initialization (default: ``False``).
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def switch_all(self, state: bool, **kwargs):
        """
        Switch all the connected devices on/off.

        :param state: True (switch on) or False (switch off).
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def test(self, count: int = 1, **kwargs):
        """
        Send a number of test messages to every node and record results.

        :param count: The number of test messages to send.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a value on the network.

        :param value_id: Select by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select value by [node_id/node_name, value_label]
        :param node_name: Select value by [node_id/node_name, value_label]
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def set_value(
        self,
        data,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
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
        raise NotImplementedError

    @action
    def set(self, entity: str, value: Any, **kwargs):
        return self.set_value(
            value_id=entity, id_on_network=entity, data=value, **kwargs
        )

    @abstractmethod
    @action
    def set_value_label(
        self,
        new_label: str,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
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
        raise NotImplementedError

    @abstractmethod
    @action
    def node_add_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Add a value to a node.

        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by label.
        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def node_remove_value(
        self,
        value_id: Optional[int] = None,
        id_on_network: Optional[str] = None,
        value_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Remove a value from a node.

        :param value_id: Select value by value_id.
        :param id_on_network: Select value by id_on_network.
        :param value_label: Select value by [node_id/node_name, value_label]
        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def node_heal(
        self,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        refresh_routes: bool = False,
        **kwargs
    ):
        """
        Heal network node by requesting the node to rediscover their neighbours.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        :param refresh_routes: Whether to perform return routes initialization. (default: ``False``).
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def node_update_neighbours(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Ask a node to update its neighbours table.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def node_network_update(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Update the controller with network information.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def node_refresh_info(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ):
        """
        Fetch up-to-date information about the node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_dimmers(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the dimmers on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_node_config(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the configuration values of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_battery_levels(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the battery levels of a node or of all the nodes on the network.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_power_levels(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the power levels of this node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_bulbs(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the bulbs/LEDs on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_switches(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the switches on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_sensors(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the sensors on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_doorlocks(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the doorlocks on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_usercodes(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the usercodes on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_thermostats(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the thermostats on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_protections(
        self, node_id: Optional[int] = None, node_name: Optional[str] = None, **kwargs
    ) -> Dict[int, Any]:
        """
        Get the protection-compatible devices on the network or associated to a node.

        :param node_id: Select node by node_id.
        :param node_name: Select node by name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_groups(self, **kwargs) -> Dict[int, Any]:
        """
        Get the groups on the network.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def get_scenes(self, **kwargs) -> Dict[str, Any]:
        """
        Get the scenes configured on the network.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def create_scene(self, label: str, **kwargs):
        """
        Create a new scene.

        :param label: Scene label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def remove_scene(
        self,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs
    ):
        """
        Remove a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def activate_scene(
        self,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs
    ):
        """
        Activate a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def set_scene_label(
        self,
        new_label: str,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs
    ):
        """
        Rename a scene/set the scene label.

        :param new_label: New label.
        :param scene_id: Select by scene_id.
        :param scene_label: Select by current scene label.
        """
        raise NotImplementedError

    @abstractmethod
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
        **kwargs
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
        """
        raise NotImplementedError

    @abstractmethod
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
        **kwargs
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
        raise NotImplementedError

    @abstractmethod
    @action
    def get_scene_values(
        self,
        scene_id: Optional[int] = None,
        scene_label: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        Get the values associated to a scene.

        :param scene_id: Select by scene_id.
        :param scene_label: Select by scene label.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def create_button(
        self,
        button_id: Union[int, str],
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Create a handheld button on a device. Only intended for bridge firmware controllers.

        :param button_id: The ID of the button.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def delete_button(
        self,
        button_id: Union[int, str],
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Delete a button association from a device. Only intended for bridge firmware controllers.

        :param button_id: The ID of the button.
        :param node_id: Filter by node_id.
        :param node_name: Filter by current node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def add_node_to_group(
        self,
        group_index: Optional[int] = None,
        group_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Add a node to a group.

        :param group_index: Select group by group index.
        :param group_label: Select group by group label.
        :param node_id: Select node by node_id.
        :param node_name: Select node by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def remove_node_from_group(
        self,
        group_index: Optional[int] = None,
        group_label: Optional[str] = None,
        node_id: Optional[int] = None,
        node_name: Optional[str] = None,
        **kwargs
    ):
        """
        Remove a node from a group.

        :param group_index: Select group by group index.
        :param group_label: Select group by group label.
        :param node_id: Select node by node_id.
        :param node_name: Select node by node name.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def create_new_primary(self, **kwargs):
        """
        Create a new primary controller on the network when the previous primary fails.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def hard_reset(self, **kwargs):
        """
        Perform a hard reset of the controller. It erases its network configuration settings.
        The controller becomes a primary controller ready to add devices to a new network.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def soft_reset(self, **kwargs):
        """
        Perform a soft reset of the controller.
        Resets a controller without erasing its network configuration settings.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def write_config(self, **kwargs):
        """
        Store the current configuration of the network to the user directory.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def on(self, device: str, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Turn on a switch on a device.

        :param device: ``id_on_network`` of the value to be switched on.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def off(self, device: str, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Turn off a switch on a device.

        :param device: ``id_on_network`` of the value to be switched off.
        """
        raise NotImplementedError

    @abstractmethod
    @action
    def toggle(self, device: str, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Toggle a switch on a device.

        :param device: ``id_on_network`` of the value to be toggled.
        """
        raise NotImplementedError


# vim:sw=4:ts=4:et:
