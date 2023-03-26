from abc import ABC, abstractmethod
from typing import Any
from typing_extensions import override

from . import EntityManager


class WriteableEntityManager(EntityManager, ABC):
    """
    Base class for integrations that support entities whose values can be set.
    """

    @abstractmethod
    def set(self, entity: str, value: Any, **kwargs):
        """
        Set the value of an entity.

        :param entity: The entity to set the value for. It's usually the ID of
            the entity provided by the plugin.
        :param value: The value to set the entity to.
        """
        raise NotImplementedError()


class SwitchEntityManager(WriteableEntityManager, ABC):
    """
    Base class for integrations that support binary switches.
    """

    @abstractmethod
    def on(self, *_, **__):
        """Turn on a device"""
        raise NotImplementedError()

    @abstractmethod
    def off(self, *_, **__):
        """Turn off a device"""
        raise NotImplementedError()

    @abstractmethod
    def toggle(self, *_, **__):
        """Toggle the state of a device (on->off or off->on)"""
        raise NotImplementedError()

    @override
    def set(self, entity: str, value: Any, **kwargs):
        method = self.on if value else self.off
        return method(entity, **kwargs)


class DimmerEntityManager(WriteableEntityManager, ABC):
    """
    Base class for integrations that support dimmers/multi-level switches.
    """


class EnumSwitchEntityManager(WriteableEntityManager, ABC):
    """
    Base class for integrations that support switches with a pre-defined,
    enum-like set of possible values.
    """
