from abc import ABC, abstractmethod

from platypush.plugins import Plugin, action


class WeatherPlugin(Plugin, ABC):
    """
    Base class for weather plugins.
    """

    @action
    @abstractmethod
    def get_current_weather(self, *args, **kwargs):
        raise NotImplementedError
