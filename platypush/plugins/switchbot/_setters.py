# pylint: disable=too-few-public-methods

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from platypush.context import get_plugin
from platypush.entities import Entity

from ._constants import DeviceType


class EntitySetter(ABC):
    """
    Base class for entity setters.

    The purpose of entity setters is to map property/values passed to
    :meth:`platypush.plugins.switchbot.SwitchbotPlugin.set_value` to native
    Switchbot device commands.
    """

    def __init__(self, entity: Entity):
        self.entity = entity
        self.device_id, self.property = self._plugin._split_device_id_and_property(
            self.entity.id
        )

    @abstractmethod
    def _set(
        self,
        value: Any,
        *args: Any,
        property: Optional[str] = None,  # pylint: disable=redefined-builtin
        **kwargs: Any,
    ):
        raise NotImplementedError()

    def __call__(
        self,
        value: Any,
        *args: Any,
        property: Optional[str] = None,  # pylint: disable=redefined-builtin
        **kwargs: Any,
    ):
        return self._set(value, *args, property=property, **kwargs)

    @property
    def _plugin(self):
        return get_plugin('switchbot')


class EntitySetterWithBinaryState(EntitySetter):
    """
    Base setter for entities with a binary on/off state.
    """

    def _set(
        self,
        value: Any,
        *_: Any,
        property: Optional[str] = None,  # pylint: disable=redefined-builtin
        **__: Any,
    ):
        if property == 'state':
            action = self._plugin.on if value else self._plugin.off
            return action(self.device_id)

        return None


class EntitySetterWithValueAsMethod(EntitySetter):
    """
    This mapper maps the value passed to
    :meth:`platypush.plugins.switchbot.SwitchbotPlugin.set_value` to plugin
    actions.

    In this case, the action value has a 1-1 mapping with the name of the
    associated plugin action.
    """

    def _set(self, value: Any, *_: Any, **__: Any):
        method = getattr(self._plugin, value, None)
        assert (
            method
        ), f'No such action available for device "{self.device_id}": "{value}"'
        return method(self.device_id)


class CurtainEntitySetter(EntitySetter):
    """
    Curtain entity setter.
    """

    def _set(self, value: Any, *_: Any, **__: Any):
        return self._plugin.set_curtain_position(self.device_id, int(value))


class HumidifierEntitySetter(EntitySetterWithBinaryState):
    """
    Humidifier entity setter.
    """

    def _set(
        self,
        value: Any,
        *args: Any,
        property: Optional[str] = None,  # pylint: disable=redefined-builtin
        **kwargs: Any,
    ):
        if property == 'state':
            return super()._set(value, *args, property=property, **kwargs)

        if property == 'child_lock':
            action = self._plugin.lock if value else self._plugin.unlock
            return action(self.device_id)

        if property in {'auto', 'nebulization_efficiency'}:
            return self._plugin.set_humidifier_efficiency(self.device_id, value)

        return None


class PlugEntitySetter(EntitySetterWithBinaryState):
    """
    Plug entity setter.
    """


class LightEntitySetter(EntitySetter):
    """
    Light entity setter.
    """

    def _set(
        self,
        value: Any,
        *_: Any,
        property: Optional[str] = None,  # pylint: disable=redefined-builtin
        **__: Any,
    ):
        assert property, 'No light property specified'
        return self._plugin.set_curtain_position(self.device_id, int(value))


# A static map of device types -> entity setters functors.
entity_setters: Dict[DeviceType, Type[EntitySetter]] = {
    DeviceType.BOT: EntitySetterWithValueAsMethod,
    DeviceType.CEILING_LIGHT: LightEntitySetter,
    DeviceType.CEILING_LIGHT_PRO: LightEntitySetter,
    DeviceType.COLOR_BULB: LightEntitySetter,
    DeviceType.CURTAIN: CurtainEntitySetter,
    DeviceType.HUMIDIFIER: HumidifierEntitySetter,
    DeviceType.LOCK: EntitySetterWithValueAsMethod,
    DeviceType.PLUG: PlugEntitySetter,
    DeviceType.PLUG_MINI_US: PlugEntitySetter,
    DeviceType.PLUG_MINI_JP: PlugEntitySetter,
    DeviceType.STRIP_LIGHT: LightEntitySetter,
}
