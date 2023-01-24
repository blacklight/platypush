from typing import Any, Callable, List, Optional, Type, Union

from pysmartthings import Attribute, Capability, Command, Device

from platypush.entities import Entity

from platypush.entities.audio import Muted, Volume
from platypush.entities.batteries import Battery
from platypush.entities.dimmers import Dimmer
from platypush.entities.motion import MotionSensor
from platypush.entities.switches import Switch


class DeviceMapper:
    """
    The purpose of these objects is to map the capabilities of SmartThings
    devices to native Platypush entities.
    """

    def __init__(
        self,
        entity_type: Type[Entity],
        capability: str,
        attribute: str,
        value_type: Type,
        set_command: Optional[Union[str, Callable[[Any], List[Any]]]] = None,
        get_value: Optional[Callable[[Device], Any]] = None,
        set_value_args: Optional[Callable[..., Any]] = None,
    ):
        self.entity_type = entity_type
        self.capability = capability
        self.set_command = set_command
        self.attribute = attribute
        self.value_type = value_type
        self.get_value = get_value if get_value else self._default_get_value

        self.set_value_args = (
            set_value_args if set_value_args else self._default_set_value_args
        )

    def _default_get_value(self, device: Device) -> Any:
        if hasattr(device.status, self.attribute):
            value = getattr(device.status, self.attribute)
        else:
            value = device.status.attributes[self.attribute].value

        return self.value_type(value)

    def _default_set_value_args(self, *values: Any) -> List[Any]:
        return [self.value_type(v) for v in values]


device_mappers: List[DeviceMapper] = [
    DeviceMapper(
        entity_type=Volume,
        capability=Capability.audio_volume,
        attribute=Attribute.volume,
        value_type=int,
        set_command=Command.set_volume,
    ),
    DeviceMapper(
        entity_type=Muted,
        capability=Capability.audio_mute,
        attribute=Attribute.mute,
        value_type=bool,
        set_command=lambda value: Command.mute if value else Command.unmute,
        set_value_args=lambda *_: [],
    ),
    DeviceMapper(
        entity_type=MotionSensor,
        capability=Capability.motion_sensor,
        attribute=Attribute.motion,
        value_type=bool,
    ),
    DeviceMapper(
        entity_type=Battery,
        capability=Capability.battery,
        attribute=Attribute.battery,
        value_type=int,
    ),
    DeviceMapper(
        entity_type=Dimmer,
        capability=Capability.switch_level,
        attribute=Attribute.level,
        value_type=int,
        set_command=Command.set_level,
    ),
    DeviceMapper(
        entity_type=Switch,
        capability=Capability.switch,
        attribute=Attribute.switch,
        value_type=bool,
        set_command=lambda value: Command.on if value else Command.off,
        set_value_args=lambda *_: [],
    ),
]


# vim:sw=4:ts=4:et:
