from datetime import datetime, timedelta
from queue import Queue
from typing import Callable, Dict, Final, List, Optional, Type

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from platypush.entities.bluetooth import BluetoothDevice
from platypush.message.event.bluetooth import (
    BluetoothDeviceConnectedEvent,
    BluetoothDeviceDisconnectedEvent,
    BluetoothDeviceFoundEvent,
    BluetoothDeviceSignalUpdateEvent,
    BluetoothDeviceEvent,
)

from platypush.context import get_bus

from .._cache import EntityCache
from ._cache import DeviceCache
from ._mappers import device_to_entity

_rssi_update_interval: Final[float] = 30.0
""" How often to trigger RSSI update events for a device. """


def _has_changed(
    old: Optional[BluetoothDevice], new: BluetoothDevice, attr: str
) -> bool:
    """
    Returns True if the given attribute has changed on the device.
    """
    if old is None:
        return False  # No previous value

    old_value = getattr(old, attr)
    new_value = getattr(new, attr)
    return old_value != new_value


def _has_been_set(
    old: Optional[BluetoothDevice], new: BluetoothDevice, attr: str, value: bool
) -> bool:
    """
    Returns True if the given attribute has changed and its new value matches
    the given value.
    """
    if not _has_changed(old, new, attr):
        return False

    new_value = getattr(new, attr)
    return new_value == value


event_matchers: Dict[
    Type[BluetoothDeviceEvent],
    Callable[[Optional[BluetoothDevice], BluetoothDevice], bool],
] = {
    BluetoothDeviceConnectedEvent: lambda old, new: _has_been_set(
        old, new, 'connected', True
    ),
    BluetoothDeviceDisconnectedEvent: lambda old, new: old is not None
    and old.connected
    and _has_been_set(old, new, 'connected', False),
    BluetoothDeviceFoundEvent: lambda old, new: old is None
    or (old.reachable is False and new.reachable is True),
    BluetoothDeviceSignalUpdateEvent: lambda old, new: (
        (new.rssi is not None or new.tx_power is not None)
        and (_has_changed(old, new, 'rssi') or _has_changed(old, new, 'tx_power'))
        and (
            not (old and old.updated_at)
            or datetime.utcnow() - old.updated_at
            >= timedelta(seconds=_rssi_update_interval)
        )
    ),
}
""" A static ``BluetoothDeviceEvent -> MatchCallback`` mapping. """


# pylint: disable=too-few-public-methods
class EventHandler:
    """
    Event handler for BLE devices.
    """

    def __init__(
        self,
        device_queue: Queue,
        device_cache: DeviceCache,
        entity_cache: EntityCache,
    ):
        """
        :param device_queue: Queue used to publish updated devices upstream.
        :param device_cache: Device cache.
        :param entity_cache: Entity cache.
        """
        self._device_queue = device_queue
        self._device_cache = device_cache
        self._entity_cache = entity_cache

    def __call__(self, device: BLEDevice, data: AdvertisementData):
        """
        Handler for Bluetooth device advertisement packets.

        1. It generates the relevant
            :class:`platypush.message.event.bluetooth.BluetoothDeviceEvent` if the
            state of the device has changed.

        2. It builds the relevant
            :class:`platypush.entity.bluetooth.BluetoothDevice` entity object
            populated with children entities that contain the supported
            properties.

        3. Publishes the updated entity to the upstream queue.

        :param device: The Bluetooth device.
        :param data: The advertised data.
        """

        events: List[BluetoothDeviceEvent] = []
        existing_entity = self._entity_cache.get(device.address)
        new_entity = device_to_entity(device, data)

        events += [
            event_type.from_device(new_entity)
            for event_type, matcher in event_matchers.items()
            if matcher(existing_entity, new_entity)
        ]

        self._device_cache.add(device)
        for event in events:
            get_bus().post(event)

        if events:
            self._device_queue.put_nowait(new_entity)
