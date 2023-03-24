from abc import ABC, abstractmethod
from collections import defaultdict
from threading import RLock
from typing import Any, Dict, Iterable, Optional, Tuple, Union
from typing_extensions import override

from platypush.entities.bluetooth import BluetoothDevice

from ._model import MajorDeviceClass


class BaseCache(ABC):
    """
    Base cache class for Bluetooth devices and entities.
    """

    _by_address: Dict[str, Any]
    """ Device cache by address. """
    _by_name: Dict[str, Any]
    """ Device cache by name. """

    def __init__(self):
        self._by_address = {}
        self._by_name = {}
        self._insert_locks = defaultdict(RLock)
        """ Locks for inserting devices into the cache. """

    @property
    @abstractmethod
    def _address_field(self) -> str:
        """
        Name of the field that contains the address of the device.
        """

    @property
    @abstractmethod
    def _name_field(self) -> str:
        """
        Name of the field that contains the name of the device.
        """

    def get(self, device: str) -> Optional[Any]:
        """
        Get a device by address or name.
        """
        dev = self._by_address.get(device)
        if not dev:
            dev = self._by_name.get(device)
        return dev

    def add(self, device: Any) -> Any:
        """
        Cache a device.
        """
        with self._insert_locks[device.address]:
            addr = getattr(device, self._address_field)
            name = getattr(device, self._name_field)
            self._by_address[addr] = device
            if name:
                self._by_name[name] = device

        return device

    def keys(self) -> Iterable[str]:
        """
        :return: All the cached device addresses.
        """
        return list(self._by_address.keys())

    def values(self) -> Iterable[Any]:
        """
        :return: All the cached device entities.
        """
        return list(self._by_address.values())

    def items(self) -> Iterable[Tuple[str, Any]]:
        """
        :return: All the cached items, as ``(address, device)`` tuples.
        """
        return list(self._by_address.items())

    def __contains__(self, device: str) -> bool:
        """
        :return: ``True`` if the entry is cached, ``False`` otherwise.
        """
        return self.get(device) is not None


class EntityCache(BaseCache):
    """
    Cache used to store scanned Bluetooth devices as :class:`BluetoothDevice`.
    """

    _by_address: Dict[str, BluetoothDevice]
    _by_name: Dict[str, BluetoothDevice]

    @property
    @override
    def _address_field(self) -> str:
        return 'address'

    @property
    @override
    def _name_field(self) -> str:
        return 'name'

    @override
    def get(self, device: Union[str, BluetoothDevice]) -> Optional[BluetoothDevice]:
        dev_filter = device.address if isinstance(device, BluetoothDevice) else device
        return super().get(dev_filter)

    @override
    def add(self, device: BluetoothDevice) -> BluetoothDevice:
        with self._insert_locks[device.address]:
            existing_device = self.get(device)
            if existing_device:
                self._merge_properties(device, existing_device)
                self._merge_children(device, existing_device)
                device = existing_device

            return super().add(device)

    @override
    def values(self) -> Iterable[BluetoothDevice]:
        return super().values()

    @override
    def items(self) -> Iterable[Tuple[str, BluetoothDevice]]:
        return super().items()

    @override
    def __contains__(self, device: Union[str, BluetoothDevice]) -> bool:
        """
        Override the default ``__contains__`` to support lookup by partial
        :class:`BluetoothDevice` objects.
        """
        return super().__contains__(device)

    def _merge_properties(
        self, device: BluetoothDevice, existing_device: BluetoothDevice
    ):
        """
        Coalesce the properties of the two device representations.
        """
        # Coalesce the major device class
        if existing_device.major_device_class == MajorDeviceClass.UNKNOWN:
            existing_device.major_device_class = device.major_device_class

        # Coalesce the other device and service classes
        for attr in ('major_service_classes', 'minor_device_classes'):
            setattr(
                existing_device,
                attr,
                list(
                    {
                        *getattr(existing_device, attr, []),
                        *getattr(device, attr, []),
                    }
                ),
            )

        # Coalesce mutually exclusive supports_* flags
        for attr in ('supports_ble', 'supports_legacy'):
            if not getattr(existing_device, attr, None):
                setattr(existing_device, attr, getattr(device, attr, None) or False)

        # Merge the connected property
        existing_device.connected = (
            device.connected
            if device.connected is not None
            else existing_device.connected
        )

        # Coalesce other manager-specific properties
        for attr in ('rssi', 'tx_power'):
            if getattr(existing_device, attr, None) is None:
                setattr(existing_device, attr, getattr(device, attr, None))

        # Coalesce the reachable flag
        if device.reachable is not None:
            existing_device.reachable = device.reachable

        # Merge the data and meta dictionaries
        for attr in ('data', 'meta'):
            setattr(
                existing_device,
                attr,
                {
                    **(getattr(existing_device, attr) or {}),
                    **(getattr(device, attr) or {}),
                },
            )

    def _merge_children(
        self, device: BluetoothDevice, existing_device: BluetoothDevice
    ):
        """
        Merge the device's children upon set without overwriting the
        existing ones.
        """
        # Map of the existing children
        existing_children = {
            child.external_id: child for child in existing_device.children
        }

        # Map of the new children
        new_children = {child.id: child for child in device.children}

        # Merge the existing children with the new ones without overwriting them
        existing_children.update(new_children)
        existing_device.children = list(existing_children.values())
