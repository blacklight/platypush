import logging
import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.plugins.weather.forecast import WeatherForecastPlugin
from platypush.message.event.weather import NewWeatherConditionEvent

class WeatherForecastBackend(Backend):
    def __init__(self, poll_seconds, **kwargs):
        super().__init__(**kwargs)
        self.poll_seconds = poll_seconds
        self.latest_update = {}

    def send_message(self, msg):
        pass

    def run(self):
        super().run()
        weather = get_plugin('weather.forecast')
        logging.info('Initialized weather forecast backend')

        while not self.should_stop():
            current_weather = weather.get_current_weather().output
            del current_weather['time']

            if current_weather != self.latest_update:
                self.bus.post(NewWeatherConditionEvent(**current_weather))

            self.latest_update = current_weather
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:

