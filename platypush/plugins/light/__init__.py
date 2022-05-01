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
    def on(self, lights=None, *args, **kwargs):
        """Turn the light on"""
        raise NotImplementedError()

    @action
    @abstractmethod
    def off(self, lights=None, *args, **kwargs):
        """Turn the light off"""
        raise NotImplementedError()

    @action
    @abstractmethod
    def toggle(self, lights=None, *args, **kwargs):
        """Toggle the light status (on/off)"""
        raise NotImplementedError()

    @action
    @abstractmethod
    def set_lights(self, lights=None, *args, **kwargs):
        """
        Set a set of properties on a set of lights.

        :param light: List of lights to set. Each item can represent a light
            name or ID.
        :param kwargs: key-value list of the parameters to set.
        """
        raise NotImplementedError()

    @action
    @abstractmethod
    def status(self, *args, **kwargs):
        """
        Get the current status of the lights.
        """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
