from abc import ABC, abstractmethod
import logging
from queue import Queue
import threading
from typing import Collection, Optional, Type, Union

from platypush.common import StoppableThread
from platypush.context import get_bus
from platypush.entities.bluetooth import BluetoothDevice
from platypush.message.event.bluetooth import BluetoothDeviceEvent

from ._cache import EntityCache
from ._types import DevicesBlacklist, RawServiceClass


class BaseBluetoothManager(StoppableThread, ABC):
    """
    Abstract interface for Bluetooth managers.
    """

    def __init__(
        self,
        interface: str,
        poll_interval: float,
        connect_timeout: float,
        scan_lock: threading.RLock,
        scan_enabled: threading.Event,
        device_queue: Queue[BluetoothDevice],
        service_uuids: Optional[Collection[RawServiceClass]] = None,
        device_cache: Optional[EntityCache] = None,
        exclude_known_noisy_beacons: bool = True,
        blacklist: Optional[DevicesBlacklist] = None,
        **kwargs,
    ):
        """
        :param interface: The Bluetooth interface to use.
        :param poll_interval: Scan interval in seconds.
        :param connect_timeout: Connection timeout in seconds.
        :param scan_lock: Lock to synchronize scanning access to the Bluetooth device.
        :param scan_enabled: Event used to enable/disable scanning.
        :param device_queue: Queue used by the ``EventHandler`` to publish
            updates with the new parsed device entities.
        :param device_cache: Cache used to keep track of discovered devices.
        :param exclude_known_noisy_beacons: Exclude known noisy beacons.
        :param blacklist: Blacklist of devices to exclude from discovery.
        """
        from ._plugins import scan_plugins

        kwargs['name'] = f'Bluetooth:{self.__class__.__name__}'
        super().__init__(**kwargs)

        self.logger = logging.getLogger(__name__)
        self.poll_interval = poll_interval
        self._interface: Optional[str] = interface
        self._connect_timeout: float = connect_timeout
        self._service_uuids: Collection[RawServiceClass] = service_uuids or []
        self._scan_lock = scan_lock
        self._scan_enabled = scan_enabled
        self._device_queue = device_queue
        self._exclude_known_noisy_beacons = exclude_known_noisy_beacons
        self._blacklist = blacklist or DevicesBlacklist()

        self._cache = device_cache or EntityCache()
        """ Cache of discovered devices. """
        self._plugins = scan_plugins(self)
        """ Plugins compatible with this manager. """

    def notify(
        self, event_type: Type[BluetoothDeviceEvent], device: BluetoothDevice, **kwargs
    ):
        """
        Notify about a device update event by posting a
        :class:`platypush.message.event.bluetooth.BluetoothDeviceEvent` event on
        the bus and pushing the updated entity upstream.
        """
        get_bus().post(event_type.from_device(device=device, **kwargs))
        self._device_queue.put_nowait(device)

    @property
    def plugins(self):
        return self._plugins

    @abstractmethod
    def connect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Pair and connect to a device by address or name.

        :param device: The device address or name.
        :param port: The Bluetooth port to use.
        :param service_uuid: The service UUID to connect to.
        :param interface: The Bluetooth interface to use (it overrides the
            default ``interface``).
        :param timeout: The connection timeout in seconds (it overrides the
            default ``connect_timeout``).
        """

    @abstractmethod
    def disconnect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
    ):
        """
        Close an active connection to a device.

        :param device: The device address or name.
        :param port: If connected to a non-BLE device, the optional port to
            disconnect. Either ``port`` or ``service_uuid`` is required for
            non-BLE devices.
        :param service_uuid: The UUID of the service to disconnect from.
        """

    @abstractmethod
    def scan(self, duration: Optional[float] = None) -> Collection[BluetoothDevice]:
        """
        Scan for Bluetooth devices nearby and return the results as a list of
        entities.

        :param duration: Scan duration in seconds (default: same as the plugin's
            `poll_interval` configuration parameter)
        """

    @abstractmethod
    def read(
        self,
        device: str,
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ) -> bytearray:
        """
        :param device: Name or address of the device to read from.
        :param service_uuid: Service UUID.
        :param interface: Bluetooth adapter name to use (default configured if None).
        :param connect_timeout: Connection timeout in seconds (default: same as the
            configured `connect_timeout`).
        """

    @abstractmethod
    def write(
        self,
        device: str,
        data: Union[bytes, bytearray],
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        """
        :param device: Name or address of the device to read from.
        :param data: Raw data to be sent.
        :param service_uuid: Service UUID.
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param connect_timeout: Connection timeout in seconds (default: same as the
            configured `connect_timeout`).
        """


# vim:sw=4:ts=4:et:
