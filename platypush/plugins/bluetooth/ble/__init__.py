import base64
from contextlib import asynccontextmanager
from threading import RLock
from typing import AsyncGenerator, Collection, List, Optional, Dict, Type, Union
from uuid import UUID

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from typing_extensions import override

from platypush.context import get_bus, get_or_create_event_loop
from platypush.entities import Entity, EntityManager
from platypush.entities.devices import Device
from platypush.message.event.bluetooth.ble import (
    BluetoothDeviceBlockedEvent,
    BluetoothDeviceConnectedEvent,
    BluetoothDeviceDisconnectedEvent,
    BluetoothDeviceFoundEvent,
    BluetoothDeviceLostEvent,
    BluetoothDevicePairedEvent,
    BluetoothDeviceTrustedEvent,
    BluetoothDeviceUnblockedEvent,
    BluetoothDeviceUnpairedEvent,
    BluetoothDeviceUntrustedEvent,
    BluetoothEvent,
)
from platypush.plugins import AsyncRunnablePlugin, action

UUIDType = Union[str, UUID]


class BluetoothBlePlugin(AsyncRunnablePlugin, EntityManager):
    """
    Plugin to interact with BLE (Bluetooth Low-Energy) devices.

    Note that the support for Bluetooth low-energy devices requires a Bluetooth
    adapter compatible with the Bluetooth 5.0 specification or higher.

    Requires:

        * **bleak** (``pip install bleak``)

    TODO: Write supported events.

    """

    # Default connection timeout (in seconds)
    _default_connect_timeout = 5

    def __init__(
        self,
        interface: Optional[str] = None,
        connect_timeout: float = _default_connect_timeout,
        device_names: Optional[Dict[str, str]] = None,
        service_uuids: Optional[Collection[UUIDType]] = None,
        **kwargs,
    ):
        """
        :param interface: Name of the Bluetooth interface to use (e.g. ``hci0``
            on Linux). Default: first available interface.
        :param connect_timeout: Timeout in seconds for the connection to a
            Bluetooth device. Default: 5 seconds.
        :param service_uuids: List of service UUIDs to discover. Default: all.
        :param device_names: Bluetooth address -> device name mapping. If not
            specified, the device's advertised name will be used, or its
            Bluetooth address. Example:

                .. code-block:: json

                    {
                        "00:11:22:33:44:55": "Switchbot",
                        "00:11:22:33:44:56": "Headphones",
                        "00:11:22:33:44:57": "Button"
                    }

        """
        super().__init__(**kwargs)

        self._interface = interface
        self._connect_timeout = connect_timeout
        self._service_uuids = service_uuids
        self._scan_lock = RLock()
        self._connections: Dict[str, BleakClient] = {}
        self._devices: Dict[str, BLEDevice] = {}
        self._device_name_by_addr = device_names or {}
        self._device_addr_by_name = {
            name: addr for addr, name in self._device_name_by_addr.items()
        }

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

    def _get_device_name(self, device: BLEDevice) -> str:
        return (
            self._device_name_by_addr.get(device.address)
            or device.name
            or device.address
        )

    def _post_event(
        self, event_type: Type[BluetoothEvent], device: BLEDevice, **kwargs
    ):
        props = device.details.get('props', {})
        get_bus().post(
            event_type(
                address=device.address,
                name=self._get_device_name(device),
                connected=props.get('Connected', False),
                paired=props.get('Paired', False),
                blocked=props.get('Blocked', False),
                trusted=props.get('Trusted', False),
                service_uuids=device.metadata.get('uuids', []),
                **kwargs,
            )
        )

    def _on_device_event(self, device: BLEDevice, _):
        event_types: List[Type[BluetoothEvent]] = []
        existing_device = self._devices.get(device.address)

        if existing_device:
            old_props = existing_device.details.get('props', {})
            new_props = device.details.get('props', {})

            if old_props.get('Paired') != new_props.get('Paired'):
                event_types.append(
                    BluetoothDevicePairedEvent
                    if new_props.get('Paired')
                    else BluetoothDeviceUnpairedEvent
                )

            if old_props.get('Connected') != new_props.get('Connected'):
                event_types.append(
                    BluetoothDeviceConnectedEvent
                    if new_props.get('Connected')
                    else BluetoothDeviceDisconnectedEvent
                )

            if old_props.get('Blocked') != new_props.get('Blocked'):
                event_types.append(
                    BluetoothDeviceBlockedEvent
                    if new_props.get('Blocked')
                    else BluetoothDeviceUnblockedEvent
                )

            if old_props.get('Trusted') != new_props.get('Trusted'):
                event_types.append(
                    BluetoothDeviceTrustedEvent
                    if new_props.get('Trusted')
                    else BluetoothDeviceUntrustedEvent
                )
        else:
            event_types.append(BluetoothDeviceFoundEvent)

        self._devices[device.address] = device

        if event_types:
            for event_type in event_types:
                self._post_event(event_type, device)
            self.publish_entities([device])

    @asynccontextmanager
    async def _connect(
        self,
        device: str,
        interface: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> AsyncGenerator[BleakClient, None]:
        dev = await self._get_device(device)
        async with BleakClient(
            dev.address,
            adapter=interface or self._interface,
            timeout=timeout or self._connect_timeout,
        ) as client:
            self._connections[dev.address] = client
            yield client
            self._connections.pop(dev.address)

    async def _read(
        self,
        device: str,
        service_uuid: UUIDType,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ) -> bytearray:
        async with self._connect(device, interface, connect_timeout) as client:
            data = await client.read_gatt_char(service_uuid)

        return data

    async def _write(
        self,
        device: str,
        data: bytes,
        service_uuid: UUIDType,
        interface: Optional[str] = None,
        connect_timeout: Optional[float] = None,
    ):
        async with self._connect(device, interface, connect_timeout) as client:
            await client.write_gatt_char(service_uuid, data)

    async def _scan(
        self,
        duration: Optional[float] = None,
        service_uuids: Optional[Collection[UUIDType]] = None,
        publish_entities: bool = False,
    ) -> Collection[Entity]:
        with self._scan_lock:
            timeout = duration or self.poll_interval or 5
            devices = await BleakScanner.discover(
                adapter=self._interface,
                timeout=timeout,
                service_uuids=list(
                    map(str, service_uuids or self._service_uuids or [])
                ),
                detection_callback=self._on_device_event,
            )

            # TODO Infer type from device.metadata['manufacturer_data']

        self._devices.update({dev.address: dev for dev in devices})
        if publish_entities:
            entities = self.publish_entities(devices)
        else:
            entities = self.transform_entities(devices)

        return entities

    @action
    def scan(
        self,
        duration: Optional[float] = None,
        service_uuids: Optional[Collection[UUIDType]] = None,
    ):
        """
        Scan for Bluetooth devices nearby.

        :param duration: Scan duration in seconds (default: same as the plugin's
            `poll_interval` configuration parameter)
        :param service_uuids: List of service UUIDs to discover. Default: all.
        """
        loop = get_or_create_event_loop()
        loop.run_until_complete(
            self._scan(duration, service_uuids, publish_entities=True)
        )

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
    def transform_entities(self, entities: Collection[BLEDevice]) -> Collection[Device]:
        return [
            Device(
                id=dev.address,
                name=self._get_device_name(dev),
            )
            for dev in entities
        ]

    @override
    async def listen(self):
        device_addresses = set()

        while True:
            entities = await self._scan()
            new_device_addresses = {e.id for e in entities}
            missing_device_addresses = device_addresses - new_device_addresses
            missing_devices = [
                dev
                for addr, dev in self._devices.items()
                if addr in missing_device_addresses
            ]

            for dev in missing_devices:
                self._post_event(BluetoothDeviceLostEvent, dev)
                self._devices.pop(dev.address, None)

            device_addresses = new_device_addresses


# vim:sw=4:ts=4:et:
