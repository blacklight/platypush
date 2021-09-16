import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.weather import NewWeatherConditionEvent


class WeatherBackend(Backend):
    """
    Abstract class for weather update backends.
    """

    def __init__(self, plugin_name: str, poll_seconds: int, **kwargs):
        """
        :param plugin_name: Name of the weather plugin to be used.
        :param poll_seconds: How often the backend should check for updates, in seconds.
        """
        super().__init__(**kwargs)
        self.plugin_name = plugin_name
        self.poll_seconds = poll_seconds
        self.latest_update = {}

    def run(self):
        super().run()
        weather = get_plugin(self.plugin_name)
        self.logger.info('Initialized {} backend'.format(self.__class__.__name__))

        while not self.should_stop():
            current_weather = weather.get_current_weather().output
            current_weather.pop('time', None)

            if current_weather != self.latest_update:
                self.bus.post(NewWeatherConditionEvent(plugin_name=self.plugin_name, **current_weather))

            self.latest_update = current_weather
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:
