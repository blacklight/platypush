import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.weather import NewWeatherConditionEvent, NewPrecipitationForecastEvent
from platypush.plugins.weather.buienradar import WeatherBuienradarPlugin


class WeatherBuienradarBackend(Backend):
    """
    Buienradar weather forecast backend. Listens for new weather or precipitation updates.

    Triggers:

        * :class:`platypush.message.event.weather.NewWeatherConditionEvent` when there is a weather condition update

    Requires:

        * The :mod:`platypush.plugins.weather.buienradar` plugin configured

    """

    def __init__(self, poll_seconds=300, **kwargs):
        super().__init__(**kwargs)
        self.poll_seconds = poll_seconds
        self.last_weather = None
        self.last_precip = None

    def run(self):
        super().run()
        plugin: WeatherBuienradarPlugin = get_plugin('weather.buienradar')
        self.logger.info('Initialized weather forecast backend')

        while not self.should_stop():
            weather = plugin.get_weather().output
            precip = plugin.get_precipitation().output
            del weather['measured']

            if precip != self.last_precip:
                self.bus.post(NewPrecipitationForecastEvent(plugin_name='weather.buienradar',
                                                            average=precip.get('average'),
                                                            total=precip.get('total'),
                                                            time_frame=precip.get('time_frame')))

            if weather != self.last_weather:
                self.bus.post(NewWeatherConditionEvent(**{
                    **weather,
                    'plugin_name': 'weather.buienradar',
                }))

            self.last_weather = weather
            self.last_precip = precip
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:
