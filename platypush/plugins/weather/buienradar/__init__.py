from typing import Optional, Dict, Any

from platypush.plugins import action
from platypush.plugins.weather import WeatherPlugin
from platypush.schemas.weather.buienradar import (
    WeatherSchema,
    PrecipitationForecastSchema,
)


class WeatherBuienradarPlugin(WeatherPlugin):  # pylint: disable=too-many-ancestors
    """
    Plugin for getting weather updates through Buienradar - a Dutch weather
    app.
    """

    def __init__(self, lat: float, long: float, time_frame: int = 120, **kwargs):
        """
        :param lat: Default latitude.
        :param long: Default longitude.
        :param time_frame: Default number of minutes to look ahead for
            precipitation forecast.
        """
        super().__init__(**kwargs)
        self.lat = lat
        self.long = long
        self.time_frame = time_frame
        self.latest_bulletin = {}

    def get_data(
        self,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        time_frame: Optional[int] = None,
    ) -> Dict[str, Any]:
        from buienradar.buienradar import get_data, parse_data  # type: ignore
        from buienradar.constants import SUCCESS, CONTENT, RAINCONTENT, DATA  # type: ignore

        lat = lat or self.lat
        long = long or self.long
        time_frame = time_frame or self.time_frame

        result = get_data(latitude=lat, longitude=long)
        if not result.get(SUCCESS):
            raise RuntimeError('Error while retrieving data')

        data = result.get(CONTENT)
        rain_data = result.get(RAINCONTENT)
        result = parse_data(data, rain_data, lat, long, time_frame)
        return result.get(DATA, {})

    def _get_current_weather(
        self, *_, lat: Optional[float] = None, long: Optional[float] = None, **__
    ):
        """
        Get the current weather conditions.

        :param lat: Weather latitude (default: configured latitude)
        :param long: Weather longitude (default: configured longitude)
        :return: .. schema:: schemas.weather.buienradar.WeatherSchema
        """
        return WeatherSchema().dump(self.get_data(lat, long, 60))

    def _get_forecast(
        self, *_, lat: Optional[float] = None, long: Optional[float] = None, **__
    ):
        return [
            {
                'datetime': weather['datetime'].isoformat(),
                **dict(WeatherSchema().dump(weather)),
            }
            for weather in self.get_data(lat, long, 60).get('forecast', [])
        ]

    @action
    def get_precipitation(
        self,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        time_frame: Optional[int] = None,
    ):
        """
        Get the precipitation forecast for the specified time frame.

        :param lat: Weather latitude (default: configured latitude)
        :param long: Weather longitude (default: configured longitude)
        :param time_frame: Time frame for the forecast in minutes (default: configured time_frame)
        """
        return PrecipitationForecastSchema().dump(
            self.get_data(lat, long, time_frame).get('precipitation_forecast', {})
        )


# vim:sw=4:ts=4:et:
