import enum
from uuid import UUID
from threading import RLock
from typing import Collection, Dict, Optional, Union

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

from platypush.context import get_or_create_event_loop
from platypush.entities import Entity, EnumSwitchEntityManager
from platypush.entities.switches import EnumSwitch
from platypush.plugins import AsyncRunnablePlugin, action


# pylint: disable=too-many-ancestors
class SwitchbotBluetoothPlugin(AsyncRunnablePlugin, EnumSwitchEntityManager):
    """
    Plugin to interact with a Switchbot (https://www.switch-bot.com/) device and
    programmatically control switches over a Bluetooth interface.

    Note that this plugin currently only supports Switchbot "bot" devices
    (mechanical switch pressers). For support for other devices, you may want
    the :class:`platypush.plugins.switchbot.SwitchbotPlugin` integration
    (which requires a Switchbot hub).

    Requires:

        * **bleak** (``pip install bleak``)

    """

    # Bluetooth UUID prefixes exposed by SwitchBot devices
    _uuid_prefixes = {
        'tx': '002',
        'rx': '003',
        'service': 'd00',
    }

    # Static list of Bluetooth UUIDs commonly exposed by SwitchBot devices.
    _uuids = {
        service: UUID(f'cba20{prefix}-224d-11e6-9fb8-0002a5d5c51b')
        for service, prefix in _uuid_prefixes.items()
    }

    class Command(enum.Enum):
        """
        Supported commands.
        """

        PRESS = b'\x57\x01\x00'
        ON = b'\x57\x01\x01'
        OFF = b'\x57\x01\x02'

    def __init__(
        self,
        connect_timeout: Optional[float] = 5,
        device_names: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        :param connect_timeout: Timeout in seconds for the connection to the
            Switchbot device. Default: 5 seconds
        :param device_names: Bluetooth address -> device name mapping. If not
            specified, the device's address will be used as a name as well.

        Example:
            .. code-block:: json

            {
                '00:11:22:33:44:55': 'My Switchbot',
                '00:11:22:33:44:56': 'My Switchbot 2',
                '00:11:22:33:44:57': 'My Switchbot 3'
            }

        """
        super().__init__(**kwargs)

        self._connect_timeout = connect_timeout if connect_timeout else 5
        self._scan_lock = RLock()
        self._devices: Dict[str, BLEDevice] = {}
        self._device_name_by_addr = device_names or {}
        self._device_addr_by_name = {
            name: addr for addr, name in self._device_name_by_addr.items()
        }

    async def _run(
        self, device: str, command: Command, uuid: Union[UUID, str] = _uuids['tx']
    ):
        """
        Run a command on a Switchbot device.

        :param device: Device name or address.
        :param command: Command to run.
        :param uuid: On which UUID the command should be sent. Default: the
            Switchbot registered ``tx`` service.
        """
        dev = await self._get_device(device)
        async with BleakClient(dev.address, timeout=self._connect_timeout) as client:
            await client.write_gatt_char(str(uuid), command.value)

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

    @action
    def press(self, device: str):
        """
        Send a press button command to a device

        :param device: Device name or address
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._run(device, self.Command.PRESS))

    @action
    def toggle(self, device, **_):
        return self.press(device)

    @action
    def on(self, device: str, **_):
        """
        Send a press-on button command to a device

        :param device: Device name or address
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._run(device, self.Command.ON))

    @action
    def off(self, device: str, **_):
        """
        Send a press-off button command to a device

        :param device: Device name or address
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._run(device, self.Command.OFF))

    @action
    # pylint: disable=arguments-differ
    def set_value(self, device: str, data: str, *_, **__):
        """
        Entity-compatible ``set_value`` method to send a command to a device.

        :param device: Device name or address
        :param data: Command to send. Possible values are:

            - ``on``: Press the button and remain in the pressed state.
            - ``off``: Release a previously pressed button.
            - ``press``: Press and release the button.

        """
        if data == 'on':
            return self.on(device)
        if data == 'off':
            return self.off(device)
        if data == 'press':
            return self.press(device)

        self.logger.warning('Unknown command for SwitchBot "%s": "%s"', device, data)
        return None

    @action
    def scan(self, duration: Optional[float] = None) -> Collection[Entity]:
        """
        Scan for available Switchbot devices nearby.

        :param duration: Scan duration in seconds (default: same as the plugin's
            `poll_interval` configuration parameter)
        :return: The list of discovered Switchbot devices.
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._scan(duration))

    @action
    def status(self, *_, **__) -> Collection[Entity]:
        """
        Alias for :meth:`.scan`.
        """
        return self.scan().output

    async def _scan(self, duration: Optional[float] = None) -> Collection[Entity]:
        with self._scan_lock:
            timeout = duration or self.poll_interval or 5
            devices = await BleakScanner.discover(timeout=timeout)
            compatible_devices = [
                d
                for d in devices
                if set(d.metadata.get('uuids', [])).intersection(
                    map(str, self._uuids.values())
                )
            ]

        new_devices = [
            dev for dev in compatible_devices if dev.address not in self._devices
        ]

        self._devices.update({dev.address: dev for dev in compatible_devices})

        entities = self.transform_entities(compatible_devices)
        self.publish_entities(new_devices)
        return entities

    def transform_entities(
        self, entities: Collection[BLEDevice]
    ) -> Collection[EnumSwitch]:
        return [
            EnumSwitch(
                id=dev.address,
                name=self._device_name_by_addr.get(dev.address, dev.name),
                value='on',
                values=['on', 'off', 'press'],
                is_write_only=True,
            )
            for dev in entities
        ]

    async def listen(self):
        while True:
            await self._scan()


# vim:sw=4:ts=4:et:
