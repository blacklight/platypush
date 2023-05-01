from datetime import datetime, timedelta
from logging import getLogger
from queue import Queue
from typing import Callable, Collection, Dict, Final, List, Optional, Type
from uuid import UUID

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from platypush.context import get_bus
from platypush.entities.bluetooth import BluetoothDevice, BluetoothService
from platypush.message.event.bluetooth import (
    BluetoothDeviceConnectedEvent,
    BluetoothDeviceDisconnectedEvent,
    BluetoothDeviceFoundEvent,
    BluetoothDeviceSignalUpdateEvent,
    BluetoothDeviceEvent,
)

from .._cache import EntityCache
from .._model import ServiceClass
from .._plugins import BaseBluetoothPlugin
from .._types import DevicesBlacklist
from ._cache import DeviceCache
from ._mappers import device_to_entity

_rssi_update_interval: Final[float] = 30.0
""" How often to trigger RSSI update events for a device. """

_excluded_manufacturers: Final[Collection[str]] = {
    'Apple Continuity',
    'Apple, Inc.',
    'GAEN',
    'Google',
    'Google Inc.',
    'Microsoft',
    'Samsung Electronics Co., Ltd',
}
"""
Exclude beacons from these device manufacturers by default (main offenders
when it comes to Bluetooth device space pollution).
"""

logger = getLogger(__name__)


def _has_changed(
    old: Optional[BluetoothDevice],
    new: BluetoothDevice,
    attr: str,
    tolerance: Optional[float] = None,
) -> bool:
    """
    Returns True if the given attribute has changed on the device.
    """
    if old is None:
        return False  # No previous value

    old_value = getattr(old, attr)
    new_value = getattr(new, attr)
    if tolerance and (old_value is not None and new_value is not None):
        return abs(new_value - old_value) < tolerance
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
    and bool(old.connected)
    and _has_been_set(old, new, 'connected', False),
    BluetoothDeviceFoundEvent: lambda old, new: old is None
    or (old.reachable is False and new.reachable is True),
    BluetoothDeviceSignalUpdateEvent: lambda old, new: (  # type: ignore
        (new.rssi is not None or new.tx_power is not None)
        and bool(old and old.rssi)
        and (
            _has_changed(old, new, 'rssi', tolerance=5)
            or _has_changed(old, new, 'tx_power', tolerance=5)
        )
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
        plugins: Collection[BaseBluetoothPlugin],
        exclude_known_noisy_beacons: bool,
        blacklist: DevicesBlacklist,
    ):
        """
        :param device_queue: Queue used to publish updated devices upstream.
        :param device_cache: Device cache.
        :param entity_cache: Entity cache.
        :param exclude_known_noisy_beacons: Exclude known noisy beacons.
        :param blacklist: Blacklist rules.
        """
        self._device_queue = device_queue
        self._device_cache = device_cache
        self._entity_cache = entity_cache
        self._plugins = plugins
        self._exclude_known_noisy_beacons = exclude_known_noisy_beacons
        self._blacklist = blacklist

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

        new_entity = device_to_entity(device, data)
        if self._exclude_known_noisy_beacons and self._is_noisy_beacon(new_entity):
            logger.debug(
                'exclude_known_noisy_beacons is set to True: skipping beacon from device %s',
                device.address,
            )
            return

        if self._blacklist.matches(new_entity):
            logger.debug('Ignoring blacklisted device: %s', device.address)
            return

        # Extend the new entity with children entities added by the plugins
        for plugin in self._plugins:
            plugin.extend_device(new_entity)

        events: List[BluetoothDeviceEvent] = []
        existing_entity = self._entity_cache.get(device.address)
        events += [
            event_type.from_device(new_entity)
            for event_type, matcher in event_matchers.items()
            if matcher(existing_entity, new_entity)
        ]

        self._device_cache.add(device)
        for event in events:
            get_bus().post(event)

        if events:
            new_entity.reachable = True  # type: ignore
            self._device_queue.put_nowait(new_entity)

    @staticmethod
    def _is_noisy_beacon(device: BluetoothDevice) -> bool:
        """
        Check if the beacon received from the given device should be skipped.
        """
        # Exclude iBeacons
        if device.model == 'iBeacon':
            return True

        # "Noisy" beacon devices usually have no associated friendly name. If a
        # device has a valid name, we should probably include it.
        if (
            device.name
            and device.name.replace('-', ':').lower() != device.address.lower()
        ):
            return False

        # If the manufacturer is in the excluded list, we should skip it
        if (
            device.manufacturer in _excluded_manufacturers
            or device.model in _excluded_manufacturers
        ):
            return True

        # If the device has no children and no manufacturer, skip it
        if not (device.children and device.manufacturer):
            return True

        # If the device has any children other than services, don't skip it
        if any(not isinstance(child, BluetoothService) for child in device.children):
            return False

        # If the device's only children are unknown services, skip it
        if not any(
            isinstance(child, BluetoothService)
            and child.service_class != ServiceClass.UNKNOWN
            for child in device.children
        ):
            return True

        mapped_uuids = [
            int(str(srv.uuid).split('-', maxsplit=1)[0], 16) & 0xFFFF
            if isinstance(srv.uuid, UUID)
            else srv.uuid
            for srv in device.services
        ]

        # If any of the services matches the blacklisted manufacturers, skip
        # the event.
        return any(
            str(ServiceClass.get(uuid)) in _excluded_manufacturers
            for uuid in mapped_uuids
        )
