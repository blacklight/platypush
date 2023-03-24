from collections import defaultdict
from contextlib import contextmanager
from queue import Empty, Queue
from threading import Event, RLock, Thread, current_thread
from typing import (
    Dict,
    Final,
    Generator,
    List,
    Optional,
    Union,
)
from typing_extensions import override

import bluetooth

from platypush.entities.bluetooth import BluetoothDevice, BluetoothService
from platypush.message.event.bluetooth import (
    BluetoothConnectionFailedEvent,
    BluetoothDeviceConnectedEvent,
    BluetoothDeviceDisconnectedEvent,
)

from ..._manager import BaseBluetoothManager
from ..._types import RawServiceClass
from .._model import BluetoothDeviceBuilder
from ._connection import BluetoothConnection
from ._service import ServiceDiscoverer
from ._types import ConnectionId


class LegacyManager(BaseBluetoothManager):
    """
    Scanner for Bluetooth non-low-energy devices.
    """

    _service_discovery_timeout: Final[int] = 30

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._connections: Dict[ConnectionId, BluetoothConnection] = {}
        """ Maps (address, port) pairs to Bluetooth connections. """
        self._connection_locks: Dict[ConnectionId, RLock] = defaultdict(RLock)
        """ Maps (address, port) pairs to connection locks. """
        self._service_scanned_devices: Dict[str, bool] = {}
        """ Maps the addresses of the devices whose services have been scanned. """

    def get_device(
        self,
        device: str,
        scan_duration: Optional[int] = None,
        _fail_if_not_cached: bool = False,
    ) -> BluetoothDevice:
        """
        Get/discover a device by its address or name.

        :param device: Device address or name.
        :param scan_duration: Overrides the duration of the scan.
        :param _fail_if_not_cached: Throw an assertion error if the device
            hasn't been cached yet.
        """
        duration = scan_duration or self.poll_interval
        dev = self._cache.get(device)
        if dev:
            return dev  # If it's already cached, just return it.

        assert not _fail_if_not_cached, f'Device "{device}" not found'

        # Otherwise, scan for the device.
        self.logger.info('Scanning for device "%s"...', device)
        self.scan(duration=duration)

        # Run the method again, but this time fail if the device has not been
        # found in the latest scan.
        return self.get_device(device, scan_duration, _fail_if_not_cached=True)

    def _get_matching_services(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
    ) -> List[BluetoothService]:
        """
        Given a device and a port or service UUID, return a list of matching
        services.
        """
        assert port or service_uuid, 'Please specify at least one of port/service_uuid'
        dev = self.get_device(device)
        assert dev, f'Device "{device}" not found'

        matching_services = []
        if port:
            matching_services = [srv for srv in dev.services if srv.port == port]
        elif service_uuid:
            uuid = BluetoothService.to_uuid(service_uuid)
            matching_services = [srv for srv in dev.services if uuid == srv.uuid]

        return matching_services

    def _connect_thread(
        self,
        conn_queue: Queue[BluetoothConnection],
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
    ):
        """
        Connection thread that asynchronously pushes a
        :class:`BluetoothConnection` object to a queue when connected, so the
        caller can wait for the connection to complete and handle timeouts.
        """
        dev = self.get_device(device)
        matching_services = self._get_matching_services(device, port, service_uuid)
        assert matching_services, (
            f'No services found on {dev.address} for '
            f'UUID={service_uuid} port={port}'
        )

        conn = BluetoothConnection(
            address=dev.address,
            service=matching_services[0],
            thread=current_thread(),
        )

        existing_conn = self._connections.get(conn.key)
        if existing_conn and existing_conn.socket:
            conn = existing_conn
        else:
            with self._connection_locks[conn.key]:
                addr = conn.address
                port_ = conn.service.port
                self.logger.info(
                    'Opening connection to device %s on port %s', addr, port_
                )

                # Connect to the specified address and port.
                conn.socket.connect((addr, port_))
                self.logger.info('Connected to device %s on port %s', addr, port_)
                self._connections[conn.key] = conn

        conn_queue.put_nowait(conn)

    @contextmanager
    def _connect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
        timeout: Optional[float] = None,
    ) -> Generator[BluetoothConnection, None, None]:
        """
        Wraps the connection thread in a context manager with timeout support.
        """
        dev = self.get_device(device)
        # Queue where the connection object is pushed once the socket is ready
        conn_queue: Queue[BluetoothConnection] = Queue()

        # Start the connection thread
        conn_thread = Thread(
            target=self._connect_thread,
            name=f'Bluetooth:connect@{device}',
            args=(conn_queue, device, port, service_uuid),
        )

        conn_thread.start()

        # Wait for the connection object
        timeout = timeout or self._connect_timeout
        try:
            conn = conn_queue.get(timeout=timeout)
        except Empty as e:
            dev.connected = False
            self.notify(BluetoothConnectionFailedEvent, dev, reason=str(e))
            raise AssertionError(f'Connection to {device} timed out') from e

        dev.connected = True
        conn.service.connected = True
        self.notify(BluetoothDeviceConnectedEvent, dev)
        yield conn

        # Close the connection once the context is over
        with self._connection_locks[conn.key]:
            try:
                conn.close()
            except Exception as e:
                self.logger.warning(
                    'Error while closing the connection to %s: %s', device, e
                )

            self._connections.pop(conn.key, None)

        dev.connected = False
        conn.service.connected = False
        self.notify(BluetoothDeviceDisconnectedEvent, dev)

    @override
    def connect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        connected = Event()

        def connect_thread():
            with self._connect(device, port, service_uuid) as conn:
                connected.set()
                conn.stop_event.wait()

            self.logger.info('Connection to %s successfully terminated', conn.address)

        # Start the connection thread
        Thread(
            target=connect_thread,
            name=f'Bluetooth:connect:wrapper@{device}',
        ).start()

        # Wait for the connected event
        timeout = timeout or self._connect_timeout
        conn_success = connected.wait(timeout=timeout)
        assert conn_success, f'Connection to {device} timed out'

    @override
    def disconnect(
        self,
        device: str,
        port: Optional[int] = None,
        service_uuid: Optional[RawServiceClass] = None,
    ):
        matching_connections = [
            conn
            for conn in self._connections.values()
            if conn.address == device
            and (port is None or conn.service.port == port)
            and (service_uuid is None or conn.service.uuid == service_uuid)
        ]

        assert matching_connections, f'No active connections found to {device}'
        for conn in matching_connections:
            conn.close()

    @override
    def scan(self, duration: Optional[float] = None) -> List[BluetoothDevice]:
        duration = duration or self.poll_interval
        assert duration, 'Scan duration must be set'
        duration = int(max(duration, 1))

        with self._scan_lock:
            # Discover all devices.
            try:
                info = bluetooth.discover_devices(
                    duration=duration, lookup_names=True, lookup_class=True
                )
            except IOError as e:
                self.logger.warning('Could not discover devices: %s', e)
                # Wait a bit before a potential retry
                self.wait_stop(timeout=1)
                return []

        # Pre-fill the services for the devices that have already been scanned.
        services: Dict[str, List[BluetoothService]] = {
            addr: self._cache.get(addr).services  # type: ignore
            for addr, _, __ in info
            if self._cache.get(addr) is not None
        }

        # Check if there are any devices that have not been scanned yet.
        unknown_devices = [
            addr
            for addr, _, __ in info
            if not self._service_scanned_devices.get(addr, False)
        ]

        # Discover the services for the devices that have not been scanned.
        if unknown_devices:
            services.update(
                ServiceDiscoverer().discover(
                    *unknown_devices, timeout=self._service_discovery_timeout
                )
            )

        # Initialize the BluetoothDevice objects.
        devices = {
            addr: BluetoothDeviceBuilder.build(
                address=addr,
                name=name,
                raw_class=class_,
                services=services.get(addr, []),
            )
            for addr, name, class_ in info
        }

        for dev in devices.values():
            self._service_scanned_devices[dev.address] = True
            if self._blacklist.matches(dev):
                self.logger.debug('Ignoring blacklisted device: %s', dev.address)
            else:
                self._device_queue.put_nowait(dev)

        return list(devices.values())

    @override
    def read(
        self,
        device: str,
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
        size: int = 1024,
    ) -> bytearray:
        """
        :param size: Number of bytes to read.
        """
        with self._connect(
            device, service_uuid=service_uuid, timeout=connect_timeout
        ) as conn:
            try:
                return conn.socket.recv(size)
            except bluetooth.BluetoothError as e:
                raise AssertionError(f'Error reading from {device}: {e}') from e

    @override
    def write(
        self,
        device: str,
        data: Union[bytes, bytearray],
        service_uuid: RawServiceClass,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        with self._connect(
            device, service_uuid=service_uuid, timeout=connect_timeout
        ) as conn:
            try:
                return conn.socket.send(data)
            except bluetooth.BluetoothError as e:
                raise AssertionError(f'Error reading from {device}: {e}') from e

    @override
    def run(self):
        super().run()
        self.logger.info('Starting legacy Bluetooth scanner')

        while not self.should_stop():
            scan_enabled = self._scan_enabled.wait(timeout=1)
            if scan_enabled:
                self.scan(duration=self.poll_interval)

    @override
    def stop(self):
        super().stop()

        # Close any active connections
        for conn in list(self._connections.values()):
            conn.close(timeout=5)

        self.logger.info('Stopped the Bluetooth legacy scanner')
