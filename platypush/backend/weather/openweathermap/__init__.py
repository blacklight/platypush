from platypush.backend.weather import WeatherBackend


class WeatherOpenweathermapBackend(WeatherBackend):
    """
    Weather forecast backend that leverages the OpenWeatherMap API.

    Requires:

        * The :class:`platypush.plugins.weather.openweathermap.WeatherOpenWeatherMapPlugin` plugin configured

    """

    def __init__(self, poll_seconds: int = 60, **kwargs):
        """
        :param poll_seconds: How often the backend should check for updates (default: every minute).
        """
        super().__init__(
            plugin_name='weather.openweathermap', poll_seconds=poll_seconds, **kwargs
        )


# vim:sw=4:ts=4:et:
