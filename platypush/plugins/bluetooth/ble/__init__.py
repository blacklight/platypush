import base64
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from threading import RLock, Timer
import threading
from time import time
from typing import (
    Any,
    AsyncGenerator,
    Collection,
    Final,
    List,
    Optional,
    Dict,
    Type,
    Union,
)
from uuid import UUID

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from typing_extensions import override

from platypush.context import get_bus, get_or_create_event_loop
from platypush.entities import Entity, EntityManager
from platypush.entities.bluetooth import BluetoothDevice
from platypush.message.event.bluetooth import (
    BluetoothDeviceBlockedEvent,
    BluetoothDeviceConnectedEvent,
    BluetoothDeviceDisconnectedEvent,
    BluetoothDeviceFoundEvent,
    BluetoothDeviceLostEvent,
    BluetoothDeviceNewDataEvent,
    BluetoothDevicePairedEvent,
    BluetoothDeviceSignalUpdateEvent,
    BluetoothDeviceTrustedEvent,
    BluetoothDeviceUnblockedEvent,
    BluetoothDeviceUnpairedEvent,
    BluetoothDeviceUntrustedEvent,
    BluetoothDeviceEvent,
    BluetoothScanPausedEvent,
    BluetoothScanResumedEvent,
)
from platypush.plugins import AsyncRunnablePlugin, action

from ._mappers import device_to_entity, parse_device_args

UUIDType = Union[str, UUID]


@dataclass
class _BluetoothConnection:
    """
    A class to store information and context about a Bluetooth connection.
    """

    client: BleakClient
    device: BLEDevice
    loop: asyncio.AbstractEventLoop
    close_event: Optional[asyncio.Event] = None
    thread: Optional[threading.Thread] = None


class BluetoothBlePlugin(AsyncRunnablePlugin, EntityManager):
    """
    Plugin to interact with BLE (Bluetooth Low-Energy) devices.

    This plugin uses `_Bleak_ <https://github.com/hbldh/bleak>`_ to interact
    with the Bluetooth stack and `_Theengs_ <https://github.com/theengs/decoder>`_
    to map the services exposed by the devices into native entities.

    The full list of devices natively supported can be found
    `here <https://decoder.theengs.io/devices/devices_by_brand.html>`_.

    Note that the support for Bluetooth low-energy devices requires a Bluetooth
    adapter compatible with the Bluetooth 5.0 specification or higher.

    Requires:

        * **bleak** (``pip install bleak``)
        * **bluetooth-numbers** (``pip install bluetooth-numbers``)
        * **TheengsGateway** (``pip install git+https://github.com/BlackLight/TheengsGateway``)

    Triggers:

        * :class:`platypush.message.event.bluetooth.BluetoothDeviceBlockedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceConnectedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceDisconnectedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceFoundEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceLostEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDevicePairedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceTrustedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceUnblockedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceUnpairedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceUntrustedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothScanPausedEvent`
        * :class:`platypush.message.event.bluetooth.BluetoothScanResumedEvent`
        * :class:`platypush.message.event.entities.EntityUpdateEvent`

    """

    _default_connect_timeout: Final[int] = 10
    """ Default connection timeout (in seconds) """

    _rssi_update_interval: Final[int] = 30
    """
    How long we should wait before triggering an update event upon a new
    RSSI update, in seconds.
    """

    def __init__(
        self,
        interface: Optional[str] = None,
        connect_timeout: float = _default_connect_timeout,
        device_names: Optional[Dict[str, str]] = None,
        uuids: Optional[Collection[UUIDType]] = None,
        scan_paused_on_start: bool = False,
        **kwargs,
    ):
        """
        :param interface: Name of the Bluetooth interface to use (e.g. ``hci0``
            on Linux). Default: first available interface.
        :param connect_timeout: Timeout in seconds for the connection to a
            Bluetooth device. Default: 10 seconds.
        :param uuids: List of service/characteristic UUIDs to discover.
            Default: all.
        :param device_names: Bluetooth address -> device name mapping. If not
            specified, the device's advertised name will be used, or its
            Bluetooth address. Example:

                .. code-block:: json

                    {
                        "00:11:22:33:44:55": "Switchbot",
                        "00:11:22:33:44:56": "Headphones",
                        "00:11:22:33:44:57": "Button"
                    }

        :param scan_paused_on_start: If ``True``, the plugin will not the
            scanning thread until :meth:`.scan_resume` is called (default:
            ``False``).

        """
        super().__init__(**kwargs)

        self._interface: Optional[str] = interface
        self._connect_timeout: float = connect_timeout
        self._uuids: Collection[Union[str, UUID]] = uuids or []
        self._scan_lock = RLock()
        self._scan_enabled = asyncio.Event()
        self._scan_controller_timer: Optional[Timer] = None
        self._connections: Dict[str, _BluetoothConnection] = {}
        self._connection_locks: Dict[str, asyncio.Lock] = {}
        self._devices: Dict[str, BLEDevice] = {}
        self._entities: Dict[str, BluetoothDevice] = {}
        self._device_last_updated_at: Dict[str, float] = {}
        self._device_name_by_addr = device_names or {}
        self._device_addr_by_name = {
            name: addr for addr, name in self._device_name_by_addr.items()
        }

        if not scan_paused_on_start:
            self._scan_enabled.set()

    async def _get_device(self, device: str) -> BLEDevice:
        """
        Utility method to get a device by name or address.
        """
        addr = (
            self._device_addr_by_name[device]
            if device in self._device_addr_by_name
            else device
        )

        if addr not in self._devices:
            self.logger.info('Scanning for unknown device "%s"', device)
            await self._scan()

        dev = self._devices.get(addr)
        assert dev is not None, f'Unknown device: "{device}"'
        return dev

    def _post_event(
        self, event_type: Type[BluetoothDeviceEvent], device: BLEDevice, **kwargs
    ):
        if event_type == BluetoothDeviceNewDataEvent:
            # Skip BluetoothDeviceNewDataEvent. They are only generated to
            # infer if the device has sent some new data, but they can be very
            # noisy and affect the latency - especially in case of connections
            # that exchange a lot of data.
            return

        get_bus().post(
            event_type(address=device.address, **parse_device_args(device), **kwargs)
        )

    def _on_device_event(self, device: BLEDevice, data: AdvertisementData):
        """
        Device advertisement packet callback handler.

        1. It generates the relevant
            :class:`platypush.message.event.bluetooth.BluetoothDeviceEvent` if the
            state of the device has changed.

        2. It builds the relevant
            :class:`platypush.entity.bluetooth.BluetoothDevice` entity object
            populated with children entities that contain the supported
            properties.

        :param device: The Bluetooth device.
        :param data: The advertisement data.
        """

        event_types: List[Type[BluetoothDeviceEvent]] = []
        entity = device_to_entity(device, data)
        existing_entity = self._entities.get(device.address)
        existing_device = self._devices.get(device.address)

        if existing_entity and existing_device:
            if existing_entity.paired != entity.paired:
                event_types.append(
                    BluetoothDevicePairedEvent
                    if entity.paired
                    else BluetoothDeviceUnpairedEvent
                )

            if existing_entity.connected != entity.connected:
                event_types.append(
                    BluetoothDeviceConnectedEvent
                    if entity.connected
                    else BluetoothDeviceDisconnectedEvent
                )

            if existing_entity.blocked != entity.blocked:
                event_types.append(
                    BluetoothDeviceBlockedEvent
                    if entity.blocked
                    else BluetoothDeviceUnblockedEvent
                )

            if existing_entity.trusted != entity.trusted:
                event_types.append(
                    BluetoothDeviceTrustedEvent
                    if entity.trusted
                    else BluetoothDeviceUntrustedEvent
                )

            if (
                time() - self._device_last_updated_at.get(device.address, 0)
            ) >= self._rssi_update_interval and (
                existing_entity.rssi != device.rssi
                or existing_entity.tx_power != entity.tx_power
            ):
                event_types.append(BluetoothDeviceSignalUpdateEvent)

            if (
                existing_device.metadata.get('manufacturer_data', {})
                != device.metadata.get('manufacturer_data', {})
            ) or (
                existing_device.details.get('props', {}).get('ServiceData', {})
                != device.details.get('props', {}).get('ServiceData', {})
            ):
                event_types.append(BluetoothDeviceNewDataEvent)
        else:
            event_types.append(BluetoothDeviceFoundEvent)

        self._devices[device.address] = device
        if device.name:
            self._device_name_by_addr[device.address] = device.name
            self._device_addr_by_name[device.name] = device.address

        if event_types:
            for event_type in event_types:
                self._post_event(event_type, device)
            self._device_last_updated_at[device.address] = time()

            # Explicitly connect the child entities to their parent before
            # flushing them
            for child in entity.children:
                child.parent = entity

            self.publish_entities([entity])

    def _has_changed(self, entity: BluetoothDevice) -> bool:
        existing_entity = self._entities.get(entity.id or entity.external_id)

        # If the entity didn't exist before, it's a new device.
        if not existing_entity:
            return True

        entity_dict = entity.to_json()
        existing_entity_dict = entity.to_json()

        # Check if any of the root attributes changed, excluding those that are
        # managed by the entities engine).
        return any(
            attr
            for attr, value in entity_dict.items()
            if value != existing_entity_dict.get(attr)
            and attr not in {'id', 'external_id', 'plugin', 'updated_at'}
        )

    @asynccontextmanager
    async def _connect(
        self,
        device: str,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
        close_event: Optional[asyncio.Event] = None,
    ) -> AsyncGenerator[_BluetoothConnection, None]:
        dev = await self._get_device(device)

        async with self._connection_locks.get(dev.address, asyncio.Lock()) as lock:
            self._connection_locks[dev.address] = lock or asyncio.Lock()

            async with BleakClient(
                dev.address,
                adapter=interface or self._interface,
                timeout=timeout or self._connect_timeout,
            ) as client:
                assert client, f'Could not connect to the device {device}'
                self.logger.info('Connected to device %s', device)
                self._connections[dev.address] = _BluetoothConnection(
                    client=client,
                    device=dev,
                    loop=asyncio.get_event_loop(),
                    thread=threading.current_thread(),
                    close_event=close_event,
                )
                yield self._connections[dev.address]
                self._connections.pop(dev.address, None)
                self.logger.info('Disconnected from device %s', device)

    async def _read(
        self,
        device: str,
        service_uuid: UUIDType,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ) -> bytearray:
        async with self._connect(device, interface, connect_timeout) as conn:
            data = await conn.client.read_gatt_char(service_uuid)

        return data

    async def _write(
        self,
        device: str,
        data: bytes,
        service_uuid: UUIDType,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        async with self._connect(device, interface, connect_timeout) as conn:
            await conn.client.write_gatt_char(service_uuid, data)

    async def _scan(
        self,
        duration: Optional[float] = None,
        uuids: Optional[Collection[UUIDType]] = None,
    ) -> Collection[Entity]:
        with self._scan_lock:
            timeout = duration or self.poll_interval or 5
            devices = await BleakScanner.discover(
                adapter=self._interface,
                timeout=timeout,
                service_uuids=list(map(str, uuids or self._uuids or [])),
                detection_callback=self._on_device_event,
            )

        self._devices.update({dev.address: dev for dev in devices})
        addresses = {dev.address.lower() for dev in devices}
        return [
            dev
            for addr, dev in self._entities.items()
            if isinstance(dev, BluetoothDevice)
            and addr.lower() in addresses
            and dev.reachable
        ]

    async def _scan_state_set(self, state: bool, duration: Optional[float] = None):
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
                self._scan_controller_timer = Timer(duration, timer_callback)
                self._scan_controller_timer.start()

    @action
    def connect(
        self,
        device: str,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Pair and connect to a device by address or name.

        :param device: The device address or name.
        :param interface: The Bluetooth interface to use (it overrides the
            default ``interface``).
        :param timeout: The connection timeout in seconds (it overrides the
            default ``connect_timeout``).
        """
        timeout = timeout or self._connect_timeout
        connected_event = threading.Event()
        close_event = asyncio.Event()
        loop = asyncio.new_event_loop()

        def connect_thread():
            async def connect_wrapper():
                async with self._connect(device, interface, timeout, close_event):
                    connected_event.set()
                    await close_event.wait()

            asyncio.set_event_loop(loop)
            loop.run_until_complete(connect_wrapper())

        loop = get_or_create_event_loop()
        connector = threading.Thread(target=connect_thread)
        connector.start()
        success = connected_event.wait(timeout=timeout)
        assert success, f'Connection to {device} timed out'

    @action
    def disconnect(self, device: str):
        """
        Close an active connection to a device.

        :param device: The device address or name.
        """
        address: Optional[str] = device
        if not self._connections.get(device):
            address = self._device_addr_by_name.get(device)

        assert address, f'Device {device} not found'
        connection = self._connections.get(address, None)
        assert connection, f'No active connections to the device {device} were found'

        if connection.close_event:
            connection.close_event.set()
        if connection.thread and connection.thread.is_alive():
            connection.thread.join(timeout=5)
        assert not (
            connection.thread and connection.thread.is_alive()
        ), f'Disconnection from {device} timed out'

    @action
    def scan_pause(self, duration: Optional[float] = None):
        """
        Pause the scanning thread.

        :param duration: For how long the scanning thread should be paused
            (default: null = indefinitely).
        """
        if self._loop:
            asyncio.ensure_future(
                self._scan_state_set(False, duration), loop=self._loop
            )

    @action
    def scan_resume(self, duration: Optional[float] = None):
        """
        Resume the scanning thread, if inactive.

        :param duration: For how long the scanning thread should be running
            (default: null = indefinitely).
        """
        if self._loop:
            asyncio.ensure_future(self._scan_state_set(True, duration), loop=self._loop)

    @action
    def scan(
        self,
        duration: Optional[float] = None,
        uuids: Optional[Collection[UUIDType]] = None,
    ):
        """
        Scan for Bluetooth devices nearby and return the results as a list of
        entities.

        :param duration: Scan duration in seconds (default: same as the plugin's
            `poll_interval` configuration parameter)
        :param uuids: List of characteristic UUIDs to discover. Default: all.
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._scan(duration, uuids))

    @action
    def read(
        self,
        device: str,
        service_uuid: UUIDType,
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
        loop = get_or_create_event_loop()
        data = loop.run_until_complete(
            self._read(device, service_uuid, interface, connect_timeout)
        )
        return base64.b64encode(data).decode()

    @action
    def write(
        self,
        device: str,
        data: Union[str, bytes],
        service_uuid: UUIDType,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        """
        Writes data to a device

        :param device: Name or address of the device to read from.
        :param data: Data to be written, either as bytes or as a base64-encoded string.
        :param service_uuid: Service UUID.
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param connect_timeout: Connection timeout in seconds (default: same as the
            configured `connect_timeout`).
        """
        loop = get_or_create_event_loop()
        if isinstance(data, str):
            data = base64.b64decode(data.encode())

        loop.run_until_complete(
            self._write(device, data, service_uuid, interface, connect_timeout)
        )

    @override
    @action
    def status(self, *_, **__) -> Collection[Entity]:
        """
        Alias for :meth:`.scan`.
        """
        return self.scan().output

    @override
    def publish_entities(
        self, entities: Optional[Collection[Any]]
    ) -> Collection[Entity]:
        self._entities.update({entity.id: entity for entity in (entities or [])})

        return super().publish_entities(entities)

    @override
    def transform_entities(
        self, entities: Collection[Union[BLEDevice, BluetoothDevice]]
    ) -> Collection[BluetoothDevice]:
        return [
            BluetoothDevice(
                id=dev.address,
                **parse_device_args(dev),
            )
            if isinstance(dev, BLEDevice)
            else dev
            for dev in entities
        ]

    @override
    async def listen(self):
        device_addresses = set()

        while True:
            await self._scan_enabled.wait()
            entities = await self._scan(uuids=self._uuids)

            new_device_addresses = {e.external_id for e in entities}
            missing_device_addresses = device_addresses - new_device_addresses
            missing_devices = [
                dev
                for addr, dev in self._devices.items()
                if addr in missing_device_addresses
            ]

            for dev in missing_devices:
                self._post_event(BluetoothDeviceLostEvent, dev)
                self._devices.pop(dev.address, None)
                self._entities.pop(dev.address, None)

            device_addresses = new_device_addresses

    @override
    def stop(self):
        if self._scan_controller_timer:
            self._scan_controller_timer.cancel()

        connections = list(self._connections.values())
        for conn in connections:
            try:
                self.disconnect(conn.device.address)
            except Exception as e:
                self.logger.warning(
                    'Error while disconnecting from %s: %s', conn.device.address, e
                )

        super().stop()


# vim:sw=4:ts=4:et:
