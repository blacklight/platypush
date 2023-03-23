from enum import Enum
from typing import Iterable
from uuid import UUID

from typing_extensions import override

from platypush.entities import Entity
from platypush.entities.bluetooth import BluetoothDevice
from platypush.entities.switches import EnumSwitch
from platypush.plugins.bluetooth.model import ServiceClass
from platypush.plugins.bluetooth._plugins import BaseBluetoothPlugin


def _make_uuid(prefix: str) -> UUID:
    """
    Utility method to create a Switchbot characteristic UUID given a hex
    prefix.
    """
    return UUID(f'cba20{prefix}-224d-11e6-9fb8-0002a5d5c51b')


class Command(Enum):
    """
    Supported commands.
    """

    PRESS = b'\x57\x01\x00'
    ON = b'\x57\x01\x01'
    OFF = b'\x57\x01\x02'


class Characteristic(Enum):
    """
    GATT characteristic UUIDs supported by Switchbot devices.
    """

    TX = _make_uuid('002')
    RX = _make_uuid('003')
    SRV = _make_uuid('d00')


# pylint: disable=too-few-public-methods
class SwitchbotPlugin(BaseBluetoothPlugin):
    """
    Implements support for Switchbot devices.
    """

    @override
    def supports_device(self, device: BluetoothDevice) -> bool:
        return any(
            srv.service_class == ServiceClass.SWITCHBOT for srv in device.services
        )

    @override
    def _extract_entities(self, device: BluetoothDevice) -> Iterable[Entity]:
        return [
            EnumSwitch(
                id=f'{device.address}::switchbot',
                name='Switchbot',
                values=[cmd.name.lower() for cmd in Command],
                is_write_only=True,
            )
        ]

    def set(self, device: BluetoothDevice, value: str, **_) -> None:
        value = value.upper()
        cmd = getattr(Command, value, None)
        assert cmd, f'No such command: {value}. Available commands: {list(Command)}.'
        self._manager.write(device.address, cmd.value, Characteristic.TX.value)
