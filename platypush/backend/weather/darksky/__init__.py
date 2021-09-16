from platypush.backend.weather import WeatherBackend


class WeatherDarkskyBackend(WeatherBackend):
    """
    Weather forecast backend that leverages the DarkSky API.

    Triggers:

        * :class:`platypush.message.event.weather.NewWeatherConditionEvent` when there is a weather condition update

    Requires:

        * The :class:`platypush.plugins.weather.darksky.WeatherDarkskyPlugin` plugin configured

    """

    def __init__(self, poll_seconds: int = 300, **kwargs):
        """
        :param poll_seconds: How often the backend should check for updates (default: every 5 minutes).
        """
        super().__init__(plugin_name='weather.darksky', poll_seconds=poll_seconds, **kwargs)


# vim:sw=4:ts=4:et:
