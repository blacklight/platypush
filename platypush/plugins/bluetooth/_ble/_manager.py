import asyncio
from contextlib import asynccontextmanager
import threading
from typing import (
    AsyncGenerator,
    Collection,
    Final,
    List,
    Optional,
    Dict,
    Union,
)

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from typing_extensions import override

from platypush.context import get_or_create_event_loop
from platypush.entities.bluetooth import BluetoothDevice
from platypush.message.event.bluetooth import (
    BluetoothConnectionFailedEvent,
    BluetoothDeviceDisconnectedEvent,
    BluetoothDeviceLostEvent,
)

from .._manager import BaseBluetoothManager
from .._types import RawServiceClass
from ._cache import DeviceCache
from ._connection import BluetoothConnection
from ._event_handler import EventHandler


class BLEManager(BaseBluetoothManager):
    """
    Integration for Bluetooth Low Energy (BLE) devices.
    """

    _rssi_update_interval: Final[int] = 30
    """
    How long we should wait before triggering an update event upon a new
    RSSI update, in seconds.
    """

    _min_get_device_scan_duration: Final[int] = 10
    """
    Wait at least this many seconds for a device to be discovered when calling
    get_device().
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._connections: Dict[str, BluetoothConnection] = {}
        """
        ``address -> BluetoothConnection`` mapping containing the active
        connections
        """
        self._connection_locks: Dict[str, asyncio.Lock] = {}
        """
        ``address -> Lock`` locks used to synchronize concurrent access to
        the devices
        """
        self._device_cache = DeviceCache()
        """ Cache of discovered ``BLEDevice`` objects. """
        self._event_handler = EventHandler(
            device_queue=self._device_queue,
            device_cache=self._device_cache,
            entity_cache=self._cache,
            plugins=self._plugins,
            blacklist=self._blacklist,
            exclude_known_noisy_beacons=self._exclude_known_noisy_beacons,
        )
        """ Bluetooth device event handler """
        self._main_loop: Optional[asyncio.AbstractEventLoop] = None
        """ Main event loop """

    async def _get_device(self, device: str) -> BLEDevice:
        """
        Utility method to get a device by name or address.
        """
        dev = self._device_cache.get(device)
        if not dev:
            self.logger.info('Scanning for unknown device "%s"', device)
            await self._scan(
                duration=max(self._min_get_device_scan_duration, self.poll_interval)
            )

            dev = self._device_cache.get(device)

        assert dev, f'Unknown device: "{device}"'
        return dev

    def _disconnected_callback(self, client: BleakClient):
        self._connections.pop(client.address, None)
        dev = self._cache.get(client.address)
        if not dev:
            return  # Unknown device

        dev.connected = False
        self.notify(BluetoothDeviceDisconnectedEvent, dev)

    @asynccontextmanager
    async def _connect(
        self,
        device: str,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
        close_event: Optional[asyncio.Event] = None,
    ) -> AsyncGenerator[BluetoothConnection, None]:
        """
        Asynchronous context manager that wraps a BLE device connection.
        """
        dev = await self._get_device(device)

        async with self._connection_locks.get(dev.address, asyncio.Lock()) as lock:
            self._connection_locks[dev.address] = lock or asyncio.Lock()

            try:
                async with BleakClient(
                    dev.address,
                    adapter=interface or self._interface,
                    timeout=timeout or self._connect_timeout,
                    disconnected_callback=self._disconnected_callback,
                ) as client:
                    entity = self._cache.get(client.address)
                    if not client:
                        if entity:
                            entity.connected = False
                            self.notify(BluetoothConnectionFailedEvent, entity)

                        raise AssertionError(
                            f'Could not connect to the device {device}'
                        )

                    # Yield the BluetoothConnection object
                    self._connections[dev.address] = BluetoothConnection(
                        client=client,
                        device=dev,
                        loop=asyncio.get_event_loop(),
                        thread=threading.current_thread(),
                        close_event=close_event,
                    )
                    yield self._connections[dev.address]
            except BleakError as e:
                raise AssertionError(f'Could not connect to the device {device}') from e

    async def _read(
        self,
        device: str,
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ) -> bytearray:
        """
        Asynchronously read the next chunk of raw bytes from a BLE device given
        a service UUID.
        """
        async with self._connect(device, interface, connect_timeout) as conn:
            try:
                data = await conn.client.read_gatt_char(service_uuid)
            except BleakError as e:
                raise AssertionError(
                    f'Could not read from the device {device}: {e}'
                ) from e

        return data

    async def _write(
        self,
        device: str,
        data: bytes,
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        """
        Asynchronously write a chunk of raw bytes to a BLE device given a
        service UUID.
        """
        async with self._connect(device, interface, connect_timeout) as conn:
            try:
                await conn.client.write_gatt_char(service_uuid, data)
            except BleakError as e:
                raise AssertionError(
                    f'Could not write to the device {device}: {e}'
                ) from e

    async def _scan(
        self,
        duration: Optional[float] = None,
        service_uuids: Optional[Collection[RawServiceClass]] = None,
    ) -> List[BluetoothDevice]:
        """
        Asynchronously scan for BLE devices and return the discovered devices
        as a list of :class:`platypush.entities.bluetooth.BluetoothDevice`
        entities.
        """
        with self._scan_lock:
            timeout = duration or self.poll_interval
            devices = await BleakScanner.discover(
                adapter=self._interface,
                timeout=timeout,
                service_uuids=list(
                    map(str, service_uuids or self._service_uuids or [])
                ),
                detection_callback=self._event_handler,
            )

        addresses = {dev.address.lower() for dev in devices}
        return [
            dev
            for addr, dev in self._cache.items()
            if addr.lower() in addresses and dev.reachable
        ]

    def _close_active_connections(self):
        """
        Terminates all active connections.
        """
        connections = list(self._connections.values())
        for conn in connections:
            try:
                self.disconnect(conn.device.address)
            except Exception as e:
                self.logger.warning(
                    'Error while disconnecting from %s: %s', conn.device.address, e
                )

    def _dbus_disconnect(self, device: BLEDevice):
        """
        Disconnect from a device using the DBus API (only available on Linux).
        This may be required if there is an active connection to the device that is not owned by the
        """
        entity = self._cache.get(device.address)
        assert entity, f'Unknown device: "{device.address}"'
        path = device.details.get('path')
        assert path, f'The device "{device.address}" has no reported system path'
        assert path.startswith('/org/bluez/'), (
            f'The device "{device.address}" is not a BlueZ device. Programmatic '
            'system disconnection is only supported on Linux'
        )

        try:
            import pydbus

            bus = pydbus.SystemBus()
            dbus_device = bus.get('org.bluez', path)
            dbus_device.Disconnect()
        except Exception as e:
            raise AssertionError(
                f'Could not disconnect from {device.address}: {e}'
            ) from e

        if entity.connected:
            entity.connected = False
            self.notify(BluetoothDeviceDisconnectedEvent, entity)

    @override
    def connect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        timeout = timeout or self._connect_timeout
        connected_event = threading.Event()
        close_event = asyncio.Event()
        loop = asyncio.new_event_loop()

        def connect_thread():
            """
            The connection thread. It wraps an asyncio loop with a connect
            context manager.
            """

            async def connect_wrapper():
                """
                The asyncio connect wrapper.
                """
                async with self._connect(device, interface, timeout, close_event):
                    connected_event.set()
                    await close_event.wait()

            asyncio.set_event_loop(loop)
            loop.run_until_complete(connect_wrapper())

        # Initialize the loop and start the connection thread
        loop = get_or_create_event_loop()
        connector = threading.Thread(
            target=connect_thread,
            name=f'Bluetooth:connect@{device}',
        )
        connector.start()

        # Wait for the connection to succeed
        success = connected_event.wait(timeout=timeout)
        assert success, f'Connection to {device} timed out'

    @override
    def disconnect(self, device: str, *_, **__):
        # Get the device
        loop = get_or_create_event_loop()
        dev = loop.run_until_complete(self._get_device(device))
        assert dev, f'Device {device} not found'

        # Check if there are any active connections
        connection = self._connections.get(dev.address, None)
        if not connection:
            # If there are no active connections in this process, try to
            # disconnect through the DBus API
            self._dbus_disconnect(dev)
            return

        # Set the close event and wait for any connection thread to terminate
        if connection.close_event:
            connection.close_event.set()
        if connection.thread and connection.thread.is_alive():
            connection.thread.join(timeout=5)
        assert not (
            connection.thread and connection.thread.is_alive()
        ), f'Disconnection from {device} timed out'

    @override
    def scan(
        self,
        duration: Optional[float] = None,
        service_uuids: Optional[Collection[RawServiceClass]] = None,
    ) -> List[BluetoothDevice]:
        """
        Scan for Bluetooth devices nearby and return the results as a list of
        entities.

        :param duration: Scan duration in seconds (default: same as the plugin's
            `poll_interval` configuration parameter)
        :param service_uuids: List of service UUIDs to discover. Default: any.
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._scan(duration, service_uuids))

    @override
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
        loop = get_or_create_event_loop()
        return loop.run_until_complete(
            self._read(device, service_uuid, interface, connect_timeout)
        )

    @override
    def write(
        self,
        device: str,
        data: Union[bytes, bytearray],
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        get_or_create_event_loop().run_until_complete(
            self._write(device, data, service_uuid, interface, connect_timeout)
        )

    async def listen(self):
        """
        Main loop listener.
        """
        self.logger.info('Starting BLE scanner')
        device_addresses = set()

        while not self.should_stop():
            self._scan_enabled.wait()
            if self.should_stop():
                break

            entities = await self._scan(service_uuids=self._service_uuids)
            new_device_addresses = {e.external_id for e in entities}
            missing_device_addresses = device_addresses - new_device_addresses
            missing_devices = [
                dev
                for addr, dev in self._cache.items()
                if addr in missing_device_addresses
            ]

            for dev in missing_devices:
                dev.reachable = False
                dev.connected = False
                self.notify(BluetoothDeviceLostEvent, dev)

            device_addresses = new_device_addresses

    @override
    def run(self):
        super().run()

        self._main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._main_loop)
        try:
            self._main_loop.run_until_complete(self.listen())
        except Exception as e:
            if not self.should_stop():
                self.logger.warning('The main loop failed unexpectedly: %s', e)
                self.logger.exception(e)
        finally:
            try:
                # Try and release the scan lock if acquired
                self._scan_lock.release()
            except Exception:
                pass

    @override
    def stop(self):
        """
        Upon stop request, it stops any pending scans and closes all active
        connections.
        """
        super().stop()
        self._close_active_connections()
        if self._main_loop and self._main_loop.is_running():
            self._main_loop.stop()

        self.logger.info('Stopped the BLE scanner')


# vim:sw=4:ts=4:et:
