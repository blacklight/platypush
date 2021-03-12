from typing import Optional

from platypush.plugins import action
from platypush.plugins.http.request import HttpRequestPlugin
from platypush.plugins.weather import WeatherPlugin


class WeatherOpenweathermapPlugin(HttpRequestPlugin, WeatherPlugin):
    base_url = 'https://api.openweathermap.org/data/2.5/weather'

    def __init__(self, token: str, location: Optional[str] = None, city_id: Optional[int] = None,
                 lat: Optional[float] = None, long: Optional[float] = None, units: str = 'metric', **kwargs):
        HttpRequestPlugin.__init__(self, method='get', output='json')
        WeatherPlugin.__init__(self, **kwargs)
        self._token = token
        self._location_query = None
        self._location_query = self._get_location_query(location=location, city_id=city_id, lat=lat, long=long)
        self.units = units

    def _get_location_query(self, location: Optional[str] = None, city_id: Optional[int] = None,
                            lat: Optional[float] = None, long: Optional[float] = None) -> dict:
        if city_id:
            return {'id': city_id}
        if lat and long:
            return {'lat': lat, 'lon': long}
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
                            lat: Optional[float] = None, long: Optional[float] = None,
                            units: Optional[str] = None, **kwargs):
        params = {
            'units': units or self.units,
            **self._get_location_query(location=location, city_id=city_id, lat=lat, long=long)
        }

        response = self.get(self.base_url, params=params).output
        return self._convert_weather_response(response)
