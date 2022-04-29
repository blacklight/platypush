from abc import ABC, abstractmethod

from platypush.entities import manages
from platypush.entities.lights import Light
from platypush.plugins import Plugin, action


@manages(Light)
class LightPlugin(Plugin, ABC):
    """
    Abstract plugin to interface your logic with lights/bulbs.
    """

    @action
    @abstractmethod
    def on(self):
        """Turn the light on"""
        raise NotImplementedError()

    @action
    @abstractmethod
    def off(self):
        """Turn the light off"""
        raise NotImplementedError()

    @action
    @abstractmethod
    def toggle(self):
        """Toggle the light status (on/off)"""
        raise NotImplementedError()

    @action
    @abstractmethod
    def status(self):
        """
        Get the current status of the lights.
        """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
