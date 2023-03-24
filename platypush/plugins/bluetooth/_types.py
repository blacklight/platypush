from dataclasses import dataclass, field
from typing import Collection, Union
from uuid import UUID

RawServiceClass = Union[UUID, int]
"""
Raw type for service classes received by pybluez.
Can be either a 16-bit integer or a UUID.
"""


@dataclass
class DevicesBlacklist:
    """
    A data class representing the rules for blacklisting devices.
    """

    addresses: Collection[str] = field(default_factory=set[str])
    """ MAC addresses to ignore. """
    names: Collection[str] = field(default_factory=set[str])
    """ Device names to ignore. """
    manufacturers: Collection[str] = field(default_factory=set[str])
    """ Manufacturers strings to ignore. """

    def __post_init__(self):
        """
        Normalize the blacklist rules.
        """
        # Normalize case-sensitivity for addresses
        self.addresses = set(map(str.lower, self.addresses))
        # Make sure that all the collections are sets
        self.names = set(self.names)
        self.manufacturers = set(self.manufacturers)

    def matches(self, device) -> bool:
        """
        :type device: :class:`platypush.entities.bluetooth.BluetoothDevice`.
        """
        return (
            device.address.lower() in self.addresses
            or device.name in self.names
            or device.manufacturer in self.manufacturers
        )
