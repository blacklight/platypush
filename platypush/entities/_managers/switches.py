from abc import ABC, abstractmethod

from . import EntityManager


class SwitchEntityManager(EntityManager, ABC):
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


class MultiLevelSwitchEntityManager(EntityManager, ABC):
    """
    Base class for integrations that support dimmers/multi-level/enum switches.

    Don't extend this class directly. Instead, use on of the available
    intermediate abstract classes - like ``DimmerEntityManager`` or
    ``EnumSwitchEntityManager``.
    """

    @abstractmethod
    def set_value(  # pylint: disable=redefined-builtin
        self, device=None, property=None, *, data=None, **__
    ):
        """Set a value"""
        raise NotImplementedError()


class DimmerEntityManager(MultiLevelSwitchEntityManager, ABC):
    """
    Base class for integrations that support dimmers/multi-level switches.
    """


class EnumSwitchEntityManager(MultiLevelSwitchEntityManager, ABC):
    """
    Base class for integrations that support switches with a pre-defined,
    enum-like set of possible values.
    """
