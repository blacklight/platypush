from typing import List, Optional

import requests

from platypush.plugins.weather import WeatherPlugin
from platypush.schemas.weather.openweathermap import WeatherSchema


class WeatherOpenweathermapPlugin(WeatherPlugin):  # pylint: disable=too-many-ancestors
    """
    OpenWeatherMap plugin.

    You'll need an API token from `OpenWeatherMap
    <https://openweathermap.org/api>`_ in order to use this API.
    """

    base_url = 'https://api.openweathermap.org/data/2.5'

    def __init__(
        self,
        token: str,
        location: Optional[str] = None,
        city_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        zip_code: Optional[str] = None,
        units: str = 'metric',
        lang: Optional[str] = None,
        **kwargs,
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
        :param lang: Language code for the weather description (default: en).
        """
        super().__init__(**kwargs)
        self._token = token
        self._location_query = None
        self._location_query = self._get_location_query(
            location=location, city_id=city_id, lat=lat, long=long, zip_code=zip_code
        )
        self.units = units
        self.lang = lang

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

    def _weather_request(
        self,
        path: str,
        *_,
        location: Optional[str] = None,
        city_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        zip_code: Optional[str] = None,
        units: Optional[str] = None,
        **__,
    ) -> dict:
        units = units or self.units
        params = {
            'appid': self._token,
            'units': units,
            'lang': self.lang,
            **self._get_location_query(
                location=location,
                city_id=city_id,
                lat=lat,
                long=long,
                zip_code=zip_code,
            ),
        }

        rs = requests.get(f'{self.base_url}/{path}', params=params, timeout=10)
        rs.raise_for_status()
        return rs.json()

    def _get_current_weather(
        self,
        *_,
        location: Optional[str] = None,
        city_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        zip_code: Optional[str] = None,
        units: Optional[str] = None,
        **__,
    ) -> dict:
        units = units or self.units
        return dict(
            WeatherSchema().dump(
                {
                    'units': units,
                    **self._weather_request(
                        'weather',
                        location=location,
                        city_id=city_id,
                        lat=lat,
                        long=long,
                        zip_code=zip_code,
                        units=units,
                    ),
                }
            )
        )

    def _get_forecast(
        self,
        *_,
        location: Optional[str] = None,
        city_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        zip_code: Optional[str] = None,
        units: Optional[str] = None,
        **__,
    ) -> List[dict]:
        units = units or self.units
        return list(
            WeatherSchema().dump(
                [
                    {
                        'units': units,
                        **data,
                    }
                    for data in self._weather_request(
                        'forecast',
                        location=location,
                        city_id=city_id,
                        lat=lat,
                        long=long,
                        zip_code=zip_code,
                        units=units,
                    ).get('list', [])
                ],
                many=True,
            )
        )
