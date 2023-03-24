import base64
import os
import re
from queue import Empty, Queue
import threading
import time
from typing import (
    Any,
    Collection,
    Dict,
    Final,
    List,
    Optional,
    Union,
    Type,
)

from typing_extensions import override

from platypush.common import StoppableThread
from platypush.context import get_bus, get_plugin
from platypush.entities import (
    EnumSwitchEntityManager,
    get_entities_engine,
)
from platypush.entities.bluetooth import BluetoothDevice, BluetoothService
from platypush.message.event.bluetooth import (
    BluetoothScanPausedEvent,
    BluetoothScanResumedEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.db import DbPlugin

from ._ble import BLEManager
from ._cache import EntityCache
from ._legacy import LegacyManager
from ._types import DevicesBlacklist, RawServiceClass
from ._manager import BaseBluetoothManager


# pylint: disable=too-many-ancestors
class BluetoothPlugin(RunnablePlugin, EnumSwitchEntityManager):
    """
    Plugin to interact with Bluetooth devices.

    This plugin uses `_Bleak_ <https://github.com/hbldh/bleak>`_ to interact
    with the Bluetooth stack and `_Theengs_ <https://github.com/theengs/decoder>`_
    to map the services exposed by the devices into native entities.

    The full list of devices natively supported can be found
    `here <https://decoder.theengs.io/devices/devices_by_brand.html>`_.

    It also supports legacy Bluetooth services, as well as the transfer of
    files.

    Note that the support for Bluetooth low-energy devices requires a Bluetooth
    adapter compatible with the Bluetooth 5.0 specification or higher.

    Requires:

        * **bleak** (``pip install bleak``)
        * **bluetooth-numbers** (``pip install bluetooth-numbers``)
        * **TheengsDecoder** (``pip install TheengsDecoder``)
        * **pydbus** (``pip install pydbus``)
        * **pybluez** (``pip install git+https://github.com/pybluez/pybluez``)

    Triggers:

        * :class:`platypush.message.event.bluetooth.BluetoothConnectionFailedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceConnectedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceDisconnectedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceFoundEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceLostEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothFileReceivedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothFileSentEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothFileTransferStartedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothScanPausedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothScanResumedEvent`
        * :class:`platypush.message.event.entities.EntityUpdateEvent`

    """

    _default_connect_timeout: Final[int] = 20
    """ Default connection timeout (in seconds) """

    _default_scan_duration: Final[float] = 10.0
    """ Default duration of a discovery session (in seconds) """

    def __init__(
        self,
        interface: Optional[str] = None,
        connect_timeout: float = _default_connect_timeout,
        service_uuids: Optional[Collection[RawServiceClass]] = None,
        scan_paused_on_start: bool = False,
        poll_interval: float = _default_scan_duration,
        exclude_known_noisy_beacons: bool = True,
        ignored_device_addresses: Optional[Collection[str]] = None,
        ignored_device_names: Optional[Collection[str]] = None,
        ignored_device_manufacturers: Optional[Collection[str]] = None,
        **kwargs,
    ):
        """
        :param interface: Name of the Bluetooth interface to use (e.g. ``hci0``
            on Linux). Default: first available interface.
        :param connect_timeout: Timeout in seconds for the connection to a
            Bluetooth device. Default: 20 seconds.
        :param service_uuids: List of service UUIDs to discover.
            Default: all.
        :param scan_paused_on_start: If ``True``, the plugin will not the
            scanning thread until :meth:`.scan_resume` is called (default:
            ``False``).
        :param exclude_known_noisy_beacons: Exclude BLE beacons from devices
            known for being very noisy. It mainly includes tracking services on
            Google, Apple, Microsoft and Samsung devices. These devices are
            also known for refreshing their MAC address very frequently, which
            may result in a large (and constantly increasing) list of devices.
            Disable this flag if you need to track BLE beacons from these
            devices, but beware that you may need periodically clean up your
            list of scanned devices.
        :param ignored_device_addresses: List of device addresses to ignore.
        :param ignored_device_names: List of device names to ignore.
        :param ignored_device_manufacturers: List of device manufacturers to
            ignore.
        """
        kwargs['poll_interval'] = poll_interval
        super().__init__(**kwargs)

        self._interface: Optional[str] = interface
        """ Default Bluetooth interface to use """
        self._connect_timeout: float = connect_timeout
        """ Connection timeout in seconds """
        self._service_uuids: Collection[RawServiceClass] = service_uuids or []
        """ UUIDs to discover """
        self._scan_lock = threading.RLock()
        """ Lock to synchronize scanning access to the Bluetooth device """
        self._scan_enabled = threading.Event()
        """ Event used to enable/disable scanning """
        self._device_queue: Queue[BluetoothDevice] = Queue()
        """
        Queue used by the Bluetooth managers to published the discovered
        Bluetooth devices.
        """
        self._device_cache = EntityCache()
        """
        Cache of the devices discovered by the plugin.
        """
        self._excluded_known_noisy_beacons = exclude_known_noisy_beacons
        """ Exclude known noisy BLE beacons. """

        self._blacklist = DevicesBlacklist(
            addresses=set(ignored_device_addresses or []),
            names=set(ignored_device_names or []),
            manufacturers=set(ignored_device_manufacturers or []),
        )
        """ Blacklist rules for the devices to ignore. """

        self._managers: Dict[Type[BaseBluetoothManager], BaseBluetoothManager] = {}
        """
        Bluetooth managers threads, one for BLE devices and one for non-BLE
        devices.
        """

        self._scan_controller_timer: Optional[threading.Timer] = None
        """ Timer used to temporarily pause the discovery process """

        if not scan_paused_on_start:
            self._scan_enabled.set()

    def _refresh_cache(self) -> None:
        # Wait for the entities engine to start
        get_entities_engine().wait_start()

        with get_plugin(DbPlugin).get_session(
            autoflush=False, autocommit=False, expire_on_commit=False
        ) as session:
            existing_devices = [d.copy() for d in session.query(BluetoothDevice).all()]

        for dev in existing_devices:
            self._device_cache.add(dev)

    def _init_bluetooth_managers(self):
        """
        Initializes the Bluetooth managers threads.
        """
        manager_args = {
            'interface': self._interface,
            'poll_interval': self.poll_interval,
            'connect_timeout': self._connect_timeout,
            'stop_event': self._should_stop,
            'scan_lock': self._scan_lock,
            'scan_enabled': self._scan_enabled,
            'device_queue': self._device_queue,
            'service_uuids': list(map(BluetoothService.to_uuid, self._service_uuids)),
            'device_cache': self._device_cache,
            'exclude_known_noisy_beacons': self._excluded_known_noisy_beacons,
            'blacklist': self._blacklist,
        }

        self._managers = {
            BLEManager: BLEManager(**manager_args),
            LegacyManager: LegacyManager(**manager_args),
        }

    def _scan_state_set(self, state: bool, duration: Optional[float] = None):
        """
        Set the state of the scanning process.

        :param state: ``True`` to enable the scanning process, ``False`` to
            disable it.
        :param duration: The duration of the pause (in seconds) or ``None``.
        """

        def timer_callback():
            if state:
                self.scan_pause()
            else:
                self.scan_resume()

            self._scan_controller_timer = None

        with self._scan_lock:
            if not state and self._scan_enabled.is_set():
                get_bus().post(BluetoothScanPausedEvent(duration=duration))
            elif state and not self._scan_enabled.is_set():
                get_bus().post(BluetoothScanResumedEvent(duration=duration))

            if state:
                self._scan_enabled.set()
            else:
                self._scan_enabled.clear()

            if duration and not self._scan_controller_timer:
                self._scan_controller_timer = threading.Timer(duration, timer_callback)
                self._scan_controller_timer.start()

    def _cancel_scan_controller_timer(self):
        """
        Cancels a scan controller timer if scheduled.
        """
        if self._scan_controller_timer:
            self._scan_controller_timer.cancel()

    def _manager_by_device(
        self,
        device: BluetoothDevice,
        port: Optional[int] = None,
        service_uuid: Optional[Union[str, RawServiceClass]] = None,
    ) -> BaseBluetoothManager:
        """
        :param device: A discovered Bluetooth device.
        :param port: The port to connect to.
        :param service_uuid: The UUID of the service to connect to.
        :return: The manager associated with the device (BLE or legacy).
        """
        # No port nor service UUID -> use the BLE manager for direct connection
        if not (port or service_uuid):
            return self._managers[BLEManager]

        uuid = BluetoothService.to_uuid(service_uuid) if service_uuid else None
        matching_services = (
            [srv for srv in device.services if srv.port == port]
            if port
            else [srv for srv in device.services if srv.uuid == uuid]
        )

        if not matching_services:
            # It could be a GATT characteristic, so try BLE
            return self._managers[BLEManager]

        srv = matching_services[0]
        return (
            self._managers[BLEManager] if srv.is_ble else self._managers[LegacyManager]
        )

    def _get_device(self, device: str, _fail_if_not_cached=False) -> BluetoothDevice:
        """
        Get a device by its address or name, and scan for it if it's not
        cached.
        """
        # If device is a compound entity ID in the format
        # ``<mac_address>:<service>``, then split the MAC address part
        m = re.match(r'^(([0-9a-f]{2}:){6}):.*', device, re.IGNORECASE)
        if m:
            device = m.group(1).rstrip(':')

        dev = self._device_cache.get(device)
        if dev:
            return dev

        assert not _fail_if_not_cached, f'Device {device} not found'
        self.logger.info('Scanning for unknown device %s', device)
        self.scan()
        return self._get_device(device, _fail_if_not_cached=True)

    @action
    def connect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[Union[RawServiceClass, str]] = None,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Pair and connect to a device by address or name.

        :param device: The device address or name.
        :param port: The port to connect to. Either ``port`` or
            ``service_uuid`` is required for non-BLE devices.
        :param service_uuid: The UUID of the service to connect to. Either
            ``port`` or ``service_uuid`` is required for non-BLE devices.
        :param interface: The Bluetooth interface to use (it overrides the
            default ``interface``).
        :param timeout: The connection timeout in seconds (it overrides the
            default ``connect_timeout``).
        """
        dev = self._get_device(device)
        manager = self._manager_by_device(dev, port=port, service_uuid=service_uuid)
        uuid = BluetoothService.to_uuid(service_uuid) if service_uuid else None
        manager.connect(
            dev.address,
            port=port,
            service_uuid=uuid,
            interface=interface,
            timeout=timeout,
        )

    @action
    def disconnect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
    ):
        """
        Close an active connection to a device.

        Note that this method can only close connections that have been
        initiated by the application. It can't close connections owned by
        other applications or agents.

        :param device: The device address or name.
        :param port: If connected to a non-BLE device, the optional port to
            disconnect.
        :param service_uuid: The optional UUID of the service to disconnect
            from, for non-BLE devices.
        """
        dev = self._get_device(device)
        uuid = BluetoothService.to_uuid(service_uuid) if service_uuid else None
        err = None
        success = False

        for manager in self._managers.values():
            try:
                manager.disconnect(dev.address, port=port, service_uuid=uuid)
                success = True
            except Exception as e:
                err = e

        assert success, f'Could not disconnect from {device}: {err}'

    @action
    def scan_pause(self, duration: Optional[float] = None):
        """
        Pause the scanning thread.

        :param duration: For how long the scanning thread should be paused
            (default: null = indefinitely).
        """
        self._scan_state_set(False, duration)

    @action
    def scan_resume(self, duration: Optional[float] = None):
        """
        Resume the scanning thread, if inactive.

        :param duration: For how long the scanning thread should be running
            (default: null = indefinitely).
        """
        self._scan_state_set(True, duration)

    @action
    def scan(
        self,
        duration: Optional[float] = None,
        devices: Optional[Collection[str]] = None,
        service_uuids: Optional[Collection[RawServiceClass]] = None,
    ) -> List[BluetoothDevice]:
        """
        Scan for Bluetooth devices nearby and return the results as a list of
        entities.

        :param duration: Scan duration in seconds (default: same as the plugin's
            `poll_interval` configuration parameter)
        :param devices: List of device addresses or names to scan for.
        :param service_uuids: List of service UUIDs to discover. Default: all.
        """
        scanned_device_addresses = set()
        duration = duration or self.poll_interval or self._default_scan_duration
        uuids = {BluetoothService.to_uuid(uuid) for uuid in (service_uuids or [])}

        for manager in self._managers.values():
            scanned_device_addresses.update(
                [
                    device.address
                    for device in manager.scan(duration=duration // len(self._managers))
                    if (not uuids or any(srv.uuid in uuids for srv in device.services))
                    and (
                        not devices
                        or device.address in devices
                        or device.name in devices
                    )
                ]
            )

        with get_plugin(DbPlugin).get_session(
            autoflush=False, autocommit=False, expire_on_commit=False
        ) as session:
            return [
                d.copy()
                for d in session.query(BluetoothDevice).all()
                if d.address in scanned_device_addresses
            ]

    @action
    def read(
        self,
        device: str,
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ) -> str:
        """
        Read a message from a device.

        :param device: Name or address of the device to read from.
        :param service_uuid: Service UUID.
        :param interface: Bluetooth adapter name to use (default configured if None).
        :param connect_timeout: Connection timeout in seconds (default: same as the
            configured `connect_timeout`).
        :return: The base64-encoded response received from the device.
        """
        dev = self._get_device(device)
        uuid = BluetoothService.to_uuid(service_uuid)
        manager = self._manager_by_device(dev, service_uuid=uuid)
        data = manager.read(
            dev.address, uuid, interface=interface, connect_timeout=connect_timeout
        )
        return base64.b64encode(data).decode()

    @action
    def write(
        self,
        device: str,
        data: str,
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        """
        Writes data to a device

        :param device: Name or address of the device to read from.
        :param data: Data to be written, as a base64-encoded string.
        :param service_uuid: Service UUID.
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param connect_timeout: Connection timeout in seconds (default: same as the
            configured `connect_timeout`).
        """
        binary_data = base64.b64decode(data.encode())
        dev = self._get_device(device)
        uuid = BluetoothService.to_uuid(service_uuid)
        manager = self._manager_by_device(dev, service_uuid=uuid)
        manager.write(
            dev.address,
            binary_data,
            service_uuid=uuid,
            interface=interface,
            connect_timeout=connect_timeout,
        )

    @override
    @action
    def set(self, entity: str, value: Any, **_):
        """
        Set the value of an entity.

        This is currently only supported for Switchbot devices, where the value
        can be one among ``on``, ``off`` and ``press``.

        :param entity: The entity to set the value for. It can be the full
            entity ID in the format ``<mac-address>::<service>``, or just
            the MAC address if the plugin supports it.
        :param value: The value to set the entity to.
        """
        device = self._get_device(entity)
        matching_plugin = next(
            iter(
                plugin
                for manager in self._managers.values()
                for plugin in manager.plugins
                if plugin.supports_device(device)
            ),
            None,
        )

        assert (
            matching_plugin is not None
        ), f'Action `set` not supported on device {entity}'

        method = getattr(matching_plugin, 'set', None)
        assert method, f'The plugin {matching_plugin} does not support `set`'
        return method(device, value)

    @action
    def send_file(
        self,
        file: str,
        device: str,
        data: Optional[Union[str, bytes, bytearray]] = None,
        binary: bool = False,
    ):
        """
        Send a file to a device that exposes an OBEX Object Push service.

        :param file: Path of the file to be sent. If ``data`` is specified
            then ``file`` should include the proposed file on the
            receiving host.
        :param data: Alternatively to a file on disk you can send raw (string
            or binary) content.
        :param device: Device address or name.
        :param binary: Set to true if data is a base64-encoded binary string.
        """
        from ._file import FileSender

        if not data:
            file = os.path.abspath(os.path.expanduser(file))
            with open(file, 'rb') as f:
                binary_data = f.read()
        elif binary:
            binary_data = base64.b64decode(
                data.encode() if isinstance(data, str) else data
            )
        elif isinstance(data, str):
            binary_data = data.encode()
        else:
            binary_data = data

        sender = FileSender(self._managers[LegacyManager])  # type: ignore
        sender.send_file(file, device, binary_data)

    @override
    @action
    def status(
        self,
        *_,
        duration: Optional[float] = None,
        devices: Optional[Collection[str]] = None,
        service_uuids: Optional[Collection[RawServiceClass]] = None,
        **__,
    ) -> List[BluetoothDevice]:
        """
        Retrieve the status of all the devices, or the matching
        devices/services.

        If scanning is currently disabled, it will enable it and perform a
        scan.

        The differences between this method and :meth:`.scan` are:

            1. :meth:`.status` will return the status of all the devices known
               to the application, while :meth:`.scan` will return the status
               only of the devices discovered in the provided time window.

            2. :meth:`.status` will not initiate a new scan if scanning is
               already enabled (it will only returned the status of the known
               devices), while :meth:`.scan` will initiate a new scan.

        :param duration: Scan duration in seconds, if scanning is disabled
            (default: same as the plugin's `poll_interval` configuration
            parameter)
        :param devices: List of device addresses or names to filter for.
            Default: all.
        :param service_uuids: List of service UUIDs to filter for. Default:
            all.
        """
        if not self._scan_enabled.is_set():
            self.scan(
                duration=duration,
                devices=devices,
                service_uuids=service_uuids,
            )

        with get_plugin(DbPlugin).get_session(
            autoflush=False, autocommit=False, expire_on_commit=False
        ) as session:
            known_devices = [
                d.copy()
                for d in session.query(BluetoothDevice).all()
                if (not devices or d.address in devices or d.name in devices)
                and (
                    not service_uuids
                    or any(str(srv.uuid) in service_uuids for srv in d.services)
                )
            ]

        # Send entity update events to keep any asynchronous clients in sync
        get_entities_engine().notify(*known_devices)
        return known_devices

    @override
    def transform_entities(
        self, entities: Collection[BluetoothDevice]
    ) -> Collection[BluetoothDevice]:
        return super().transform_entities(entities)

    @override
    def main(self):
        self._refresh_cache()
        self._init_bluetooth_managers()

        for manager in self._managers.values():
            manager.start()

        try:
            while not self.should_stop():
                try:
                    device = self._device_queue.get(timeout=1)
                except Empty:
                    continue

                device = self._device_cache.add(device)
                self.publish_entities([device], callback=self._device_cache.add)
        finally:
            self.stop()

    @override
    def stop(self):
        """
        Upon stop request, it stops any pending scans and closes all active
        connections.
        """
        super().stop()

        self._cancel_scan_controller_timer()
        self._stop_threads(self._managers.values())

    def _stop_threads(self, threads: Collection[StoppableThread], timeout: float = 5):
        """
        Set the stop events on active threads and wait for them to stop.
        """
        # Set the stop events and call `.stop`
        for thread in threads:
            if thread and thread.is_alive():
                self.logger.info('Waiting for %s to stop', thread.name)
                try:
                    thread.stop()
                except Exception as e:
                    self.logger.exception('Error while stopping %s: %s', thread.name, e)

        # Wait for the manager threads to stop
        wait_start = time.time()

        for thread in threads:
            if (
                thread
                and thread.ident != threading.current_thread().ident
                and thread.is_alive()
            ):
                thread.join(timeout=max(0, timeout - (time.time() - wait_start)))

                if thread and thread.is_alive():
                    self.logger.warning(
                        'Timeout while waiting for %s to stop', thread.name
                    )


__all__ = ["BluetoothPlugin"]


# vim:sw=4:ts=4:et:
