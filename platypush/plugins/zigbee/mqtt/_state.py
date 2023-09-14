from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Union


class BridgeState(Enum):
    """
    Known bridge states.
    """

    ONLINE = 'online'
    OFFLINE = 'offline'


@dataclass
class ZigbeeDevices:
    """
    Cached information about the devices on the network.
    """

    by_address: Dict[str, dict] = field(default_factory=dict)
    by_name: Dict[str, dict] = field(default_factory=dict)

    def __contains__(self, name: str) -> bool:
        """
        :return: True if the device with the given name exists in the cache.
        """
        return name in self.by_name or name in self.by_address

    def get(self, name: str) -> Optional[dict]:
        """
        Retrieves a cached device record either by name or by address.
        """
        return self.by_address.get(name, self.by_name.get(name))

    def add(self, device: dict):
        """
        Adds a device record to the cache.
        """
        if device.get('ieee_address'):
            self.by_address[device['ieee_address']] = device
        if device.get('friendly_name'):
            self.by_name[device['friendly_name']] = device
        if not device.get('state'):
            device['state'] = {}

    def remove(self, device: Union[str, dict]):
        """
        Removes a device record from the cache.
        """
        if isinstance(device, str):
            dev = self.get(device)
            if not dev:
                return  # No such device
        else:
            dev = device

        if dev.get('ieee_address'):
            self.by_address.pop(dev['ieee_address'], None)

        if dev.get('friendly_name'):
            self.by_name.pop(dev['friendly_name'], None)

    def set_state(self, device: str, state: dict):
        """
        Updates the state of a device in the cache.

        :param device: Name or address of the device.
        :param state: Map containing the new state.
        """
        dev = self.get(device)
        if not dev:
            return

        dev['state'] = state


@dataclass
class ZigbeeState:
    """
    Cached information about the devices and groups on the network.
    """

    devices: ZigbeeDevices = field(default_factory=ZigbeeDevices)
    groups: Dict[str, dict] = field(default_factory=dict)
    bridge_state: BridgeState = BridgeState.OFFLINE
