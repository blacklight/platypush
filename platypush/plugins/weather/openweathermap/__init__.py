from typing import Optional

import requests

from platypush.plugins import action
from platypush.plugins.weather import WeatherPlugin
from platypush.schemas.weather.openweathermap import WeatherSchema


class WeatherOpenweathermapPlugin(WeatherPlugin):
    """
    OpenWeatherMap plugin.

    You'll need an API token from `OpenWeatherMap
    <https://openweathermap.org/api>`_ in order to use this API.
    """

    base_url = 'https://api.openweathermap.org/data/2.5/weather'

    def __init__(
        self,
        token: str,
        location: Optional[str] = None,
        city_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        zip_code: Optional[str] = None,
        units: str = 'metric',
        **kwargs
    ):
        """
        :param token: OpenWeatherMap API token.
        :param location: If set, then this location will be used by default for
            weather lookup. If multiple locations share the same name you can
            disambiguate by specifying the country code as well - e.g.
            ``London,GB``.
        :param city_id: If set, then this city ID will be used by default for
            weather lookup. The full list of city IDs is available `here
            <https://bulk.openweathermap.org/sample/>`_.
        :param lat: If lat/long are set, then the weather by default will be
            retrieved for the specified geo location.
        :param long: If lat/long are set, then the weather by default will be
            retrieved for the specified geo location.
        :param zip_code: If set, then this ZIP code (should be in the form
            ``zip,country_code``) will be used by default for weather lookup.
        :param units: Supported: ``metric`` (default), ``standard`` and
            ``imperial``.
        :param poll_interval: How often the weather should be refreshed, in
            seconds.
        """
        super().__init__(**kwargs)
        self._token = token
        self._location_query = None
        self._location_query = self._get_location_query(
            location=location, city_id=city_id, lat=lat, long=long, zip_code=zip_code
        )
        self.units = units

    def _get_location_query(
        self,
        location: Optional[str] = None,
        city_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        zip_code: Optional[str] = None,
    ) -> dict:
        if city_id:
            return {'id': city_id}
        if lat and long:
            return {'lat': lat, 'lon': long}
        if zip_code:
            return {'zip': zip_code}
        if location:
            return {'q': location}

        assert self._location_query, 'Specify either location, city_id or lat/long'
        return self._location_query

    @action
    def get_current_weather(
        self,
        *_,
        location: Optional[str] = None,
        city_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        zip_code: Optional[str] = None,
        units: Optional[str] = None,
        **__
    ) -> dict:
        """
        Returns the current weather.

        :param location: Override the ``location`` configuration value.
        :param city_id: Override the ``city_id`` configuration value.
        :param lat: Override the ``lat`` configuration value.
        :param long: Override the ``long`` configuration value.
        :param zip_code: Override the ``zip_code`` configuration value.
        :param units: Override the ``units`` configuration value.
        :return: .. schema:: weather.openweathermap.WeatherSchema
        """
        params = {
            'appid': self._token,
            'units': units or self.units,
            **self._get_location_query(
                location=location,
                city_id=city_id,
                lat=lat,
                long=long,
                zip_code=zip_code,
            ),
        }

        rs = requests.get(self.base_url, params=params, timeout=10)
        rs.raise_for_status()
        return dict(WeatherSchema().dump(rs.json()))
