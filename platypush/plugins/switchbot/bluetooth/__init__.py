import enum
from typing import Any, Collection, Optional
from uuid import UUID

from bleak.backends.device import BLEDevice
from typing_extensions import override

from platypush.context import get_or_create_event_loop
from platypush.entities import EnumSwitchEntityManager
from platypush.entities.switches import EnumSwitch
from platypush.plugins import action
from platypush.plugins.bluetooth.ble import BluetoothBlePlugin, UUIDType


class Command(enum.Enum):
    """
    Supported commands.
    """

    PRESS = b'\x57\x01\x00'
    ON = b'\x57\x01\x01'
    OFF = b'\x57\x01\x02'


# pylint: disable=too-many-ancestors
class SwitchbotBluetoothPlugin(BluetoothBlePlugin, EnumSwitchEntityManager):
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

    # Map of service names -> UUID prefixes exposed by SwitchBot devices
    _uuid_prefixes = {
        'tx': '002',
        'rx': '003',
        'service': 'd00',
    }

    # Static list of Bluetooth service UUIDs commonly exposed by SwitchBot
    # devices.
    _uuids = {
        service: UUID(f'cba20{prefix}-224d-11e6-9fb8-0002a5d5c51b')
        for service, prefix in _uuid_prefixes.items()
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, service_uuids=self._uuids.values(), **kwargs)

    async def _run(
        self,
        device: str,
        command: Command,
        service_uuid: UUIDType = _uuids['tx'],
    ):
        await self._write(device, command.value, service_uuid)

    @action
    def press(self, device: str):
        """
        Send a press button command to a device

        :param device: Device name or address
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._run(device, Command.PRESS))

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
        return loop.run_until_complete(self._run(device, Command.ON))

    @action
    def off(self, device: str, **_):
        """
        Send a press-off button command to a device

        :param device: Device name or address
        """
        loop = get_or_create_event_loop()
        return loop.run_until_complete(self._run(device, Command.OFF))

    @action
    def set_value(self, device: Optional[str] = None, value: Optional[str] = None, **_):
        """
        Send a command to a device as a value.

        :param entity: Device name or address
        :param value: Command to send. Possible values are:

            - ``on``: Press the button and remain in the pressed state.
            - ``off``: Release a previously pressed button.
            - ``press``: Press and release the button.

        """
        assert device, 'No device specified'
        if value == 'on':
            self.on(device)
        if value == 'off':
            self.off(device)
        if value == 'press':
            self.press(device)

        self.logger.warning('Unknown command for SwitchBot "%s": "%s"', device, value)

    @override
    def set(self, entity: str, value: Any, attribute: Optional[str] = None, **kwargs):
        return self.set_value(entity, value, **kwargs)

    @override
    def transform_entities(
        self, entities: Collection[BLEDevice]
    ) -> Collection[EnumSwitch]:
        devices = super().transform_entities(entities)
        return [
            EnumSwitch(
                id=dev.id,
                name=dev.name,
                value=None,
                values=['on', 'off', 'press'],
                is_write_only=True,
            )
            for dev in devices
        ]


# vim:sw=4:ts=4:et:
