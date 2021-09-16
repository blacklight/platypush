from typing import Optional

from platypush.plugins import action
from platypush.plugins.http.request import HttpRequestPlugin
from platypush.plugins.weather import WeatherPlugin


class WeatherOpenweathermapPlugin(HttpRequestPlugin, WeatherPlugin):
    """
    OpenWeatherMap plugin. This is the advised plugin to use for weather forecasts since Darksky has officially
    shut down their API.

    You'll need an API token from `OpenWeatherMap <https://openweathermap.org/api>`_ in order to use this API.
    """
    base_url = 'https://api.openweathermap.org/data/2.5/weather'

    def __init__(self, token: str, location: Optional[str] = None, city_id: Optional[int] = None,
                 lat: Optional[float] = None, long: Optional[float] = None,
                 zip_code: Optional[str] = None, units: str = 'metric', **kwargs):
        """
        :param token: OpenWeatherMap API token.
        :param location: If set, then this location will be used by default for weather lookup. If multiple locations
            share the same name you can disambiguate by specifying the country code as well - e.g. ``London,GB``.
        :param city_id: If set, then this city ID will be used by default for weather lookup. The full list of city IDs
            is available `here <https://bulk.openweathermap.org/sample/>`_.
        :param lat: If lat/long are set, then the weather by default will be retrieved for the specified geo location.
        :param long: If lat/long are set, then the weather by default will be retrieved for the specified geo location.
        :param zip_code: If set, then this ZIP code (should be in the form ``zip,country_code``) will be used by default
            for weather lookup.
        :param units: Supported: ``metric`` (default), ``standard`` and ``imperial``.
        """
        super().__init__(method='get', output='json', **kwargs)
        self._token = token
        self._location_query = None
        self._location_query = self._get_location_query(location=location, city_id=city_id, lat=lat, long=long,
                                                        zip_code=zip_code)
        self.units = units

    def _get_location_query(self, location: Optional[str] = None, city_id: Optional[int] = None,
                            lat: Optional[float] = None, long: Optional[float] = None,
                            zip_code: Optional[str] = None) -> dict:
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
    def get(self, url, **kwargs):
        kwargs['params'] = {
            'appid': self._token,
            **kwargs.get('params', {}),
        }

        return super().get(url, **kwargs)

    @staticmethod
    def _convert_percentage(perc: Optional[float]) -> Optional[float]:
        if perc is None:
            return
        return perc / 100.

    @staticmethod
    def _m_to_km(m: Optional[float]) -> Optional[float]:
        if m is None:
            return
        return m / 1000.

    @staticmethod
    def _get_precip_type(response: dict) -> Optional[str]:
        if response.get('snow', {}).get('1h', 0) > 0:
            return 'snow'
        if response.get('rain', {}).get('1h', 0) > 0:
            return 'rain'
        return

    @classmethod
    def _convert_weather_response(cls, response: dict) -> dict:
        return {
            'time': response.get('dt'),
            'summary': response.get('weather', [{'main': 'Unknown'}])[0].get('main', 'Unknown'),
            'icon': response.get('weather', [{'icon': 'unknown'}])[0].get('icon', 'unknown'),
            'precipIntensity': response.get('rain', response.get('snow', {})).get('1h', 0),
            'precipType': cls._get_precip_type(response),
            'temperature': response.get('main', {}).get('temp'),
            'apparentTemperature': response.get('main', {}).get('feels_like'),
            'humidity': cls._convert_percentage(response.get('main', {}).get('humidity')),
            'pressure': response.get('main', {}).get('pressure'),
            'windSpeed': response.get('wind', {}).get('speed'),
            'windDirection': response.get('wind', {}).get('deg'),
            'windGust': response.get('wind', {}).get('gust'),
            'cloudCover': cls._convert_percentage(response.get('clouds', {}).get('all')),
            'visibility': cls._m_to_km(response.get('visibility')),
            'sunrise': response.get('sys', {}).get('sunrise'),
            'sunset': response.get('sys', {}).get('sunset'),
        }

    @action
    def get_current_weather(self, *, location: Optional[str] = None, city_id: Optional[int] = None,
                            lat: Optional[float] = None, long: Optional[float] = None, zip_code: Optional[str] = None,
                            units: Optional[str] = None, **kwargs) -> dict:
        """
        Returns the current weather.

        :param location: Override the ``location`` configuration value.
        :param city_id: Override the ``city_id`` configuration value.
        :param lat: Override the ``lat`` configuration value.
        :param long: Override the ``long`` configuration value.
        :param zip_code: Override the ``zip_code`` configuration value.
        :param units: Override the ``units`` configuration value.
        """
        params = {
            'units': units or self.units,
            **self._get_location_query(location=location, city_id=city_id, lat=lat, long=long)
        }

        response = self.get(self.base_url, params=params).output
        return self._convert_weather_response(response)
