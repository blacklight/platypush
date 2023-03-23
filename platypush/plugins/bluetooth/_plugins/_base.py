from abc import ABC, abstractmethod
from typing import Iterable

from platypush.entities import Entity
from platypush.entities.bluetooth import BluetoothDevice
from platypush.plugins.bluetooth._manager import BaseBluetoothManager


class BaseBluetoothPlugin(ABC):
    """
    Base class for Bluetooth plugins, like Switchbot or HID integrations.
    """

    def __init__(self, manager: BaseBluetoothManager):
        self._manager = manager

    @abstractmethod
    def supports_device(self, device: BluetoothDevice) -> bool:
        """
        Returns True if the given device matches this plugin.
        """

    @abstractmethod
    def _extract_entities(self, device: BluetoothDevice) -> Iterable[Entity]:
        """
        If :meth:`_matches_device` returns True, this method should return an
        iterable of entities that will be used to extend the existing device -
        like sensors, switches etc.
        """

    def extend_device(self, device: BluetoothDevice):
        """
        Extends the given device with entities extracted through
        :meth:`_extract_entities`, if :meth:`_matches_device` returns True.
        """
        if not self.supports_device(device):
            return

        device.children.extend(self._extract_entities(device))
