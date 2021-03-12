from abc import ABC

from platypush.plugins import Plugin, action


class WeatherPlugin(Plugin, ABC):
    """
    Base class for weather plugins.
    """

    @action
    def get_current_weather(self, *args, **kwargs):
        raise NotImplementedError
