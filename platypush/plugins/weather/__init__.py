from abc import ABC, abstractmethod
from threading import RLock
from typing import Dict, List, Optional, Tuple

import requests

from platypush.entities.managers.weather import WeatherEntityManager

from platypush.message.event.weather import (
    NewWeatherConditionEvent,
    NewWeatherForecastEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.utils import get_plugin_name_by_class


class WeatherPlugin(RunnablePlugin, WeatherEntityManager, ABC):
    """
    Base class for weather plugins.
    """

    _geocode_url = 'https://nominatim.openstreetmap.org/search'
    _geocode_cache_size = 100

    def __init__(self, poll_interval: Optional[float] = 120, **kwargs):
        super().__init__(poll_interval=poll_interval, **kwargs)
        self._latest_weather = None
        self._latest_forecast = None
        self._geocode_cache: Dict[Tuple[str, int], List[dict]] = {}
        self._geocode_cache_lock = RLock()

    def _on_weather_data(self, weather: dict, always_publish: bool = False):
        if weather != self._latest_weather or always_publish:
            self._bus.post(
                NewWeatherConditionEvent(
                    plugin_name=get_plugin_name_by_class(self.__class__), **weather
                )
            )

            self.publish_entities([weather], type='weather')

        self._latest_weather = weather

    def _on_weather_forecast(self, forecast: List[dict], always_publish: bool = False):
        if forecast != self._latest_forecast or always_publish:
            self._bus.post(
                NewWeatherForecastEvent(
                    plugin_name=get_plugin_name_by_class(self.__class__),
                    forecast=forecast,
                )
            )

            self.publish_entities(forecast, type='forecast')

        self._latest_forecast = forecast

    @action
    def get_current_weather(
        self,
        *args,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        units: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Returns the current weather.

        :param lat: Override the ``lat`` configuration value.
        :param long: Override the ``long`` configuration value.
        :param units: Override the ``units`` configuration value.
        :return: .. schema:: weather.openweathermap.WeatherSchema
        """
        weather = self._get_current_weather(
            *args, lat=lat, long=long, units=units, **kwargs
        )
        self._on_weather_data(weather, always_publish=True)
        return weather

    @action
    def get_forecast(
        self,
        *args,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        units: Optional[str] = None,
        **kwargs,
    ) -> List[dict]:
        """
        Returns the weather forecast for the upcoming hours/days.

        :param lat: Override the ``lat`` configuration value.
        :param long: Override the ``long`` configuration value.
        :param units: Override the ``units`` configuration value.
        :return: .. schema:: weather.openweathermap.WeatherSchema(many=True)
        """
        forecast = self._get_forecast(*args, lat=lat, long=long, units=units, **kwargs)

        if forecast:
            self._on_weather_forecast(forecast, always_publish=True)

        return forecast

    @action
    def lookup_location(self, location: str, limit: int = 10) -> List[dict]:
        """
        Look up the geo-coordinates of a location by free-text query, using
        the `Nominatim <https://nominatim.org/release-docs/latest/api/Search/>`_
        OpenStreetMap API. Results are cached to limit the impact on the
        upstream service.

        :param location: Free-text location query - e.g. ``Bruxelles`` or
            ``1600 Pennsylvania Avenue, Washington DC``.
        :param limit: Maximum number of results to return (default: 10).
        :return: A list of matching locations, in the format:

            .. code-block:: json

                [
                    {
                        "name": "Brussels, Brussels-Capital, Belgium",
                        "lat": 50.8465573,
                        "long": 4.351697,
                        "type": "city"
                    }
                ]

        """
        return self._lookup_location(location, limit=limit)

    def _lookup_location(self, location: str, limit: int = 10) -> List[dict]:
        cache_key = (location.strip().lower(), limit)
        with self._geocode_cache_lock:
            cached = self._geocode_cache.get(cache_key)
            if cached is not None:
                return cached

        rs = requests.get(
            self._geocode_url,
            params={'q': location, 'format': 'json', 'limit': limit},
            headers={'User-Agent': 'platypush'},
            timeout=10,
        )

        rs.raise_for_status()
        results = [
            {
                'name': result.get('display_name'),
                'lat': float(result['lat']),
                'long': float(result['lon']),
                'type': result.get('type'),
            }
            for result in rs.json()
            if result.get('lat') is not None and result.get('lon') is not None
        ]

        with self._geocode_cache_lock:
            if len(self._geocode_cache) >= self._geocode_cache_size:
                # Drop the oldest cached entry
                self._geocode_cache.pop(next(iter(self._geocode_cache)))

            self._geocode_cache[cache_key] = results

        return results

    @action
    def status(self, *args, **kwargs) -> dict:
        """
        :return: .. schema:: weather.openweathermap.WeatherReportSchema
        """
        return self._status(*args, **kwargs)

    def _status(self, *args, **kwargs) -> dict:
        # NOTE: get_current_weather and get_forecast already return data
        # serialized through the plugin's WeatherSchema. Running the result
        # through WeatherReportSchema again would serialize it twice - the
        # nested schemas expect the raw API payload, not the already-dumped
        # representation - resulting in all the fields being reset to their
        # default values.
        return {
            'current': self.get_current_weather(*args, **kwargs).output,
            'forecast': self.get_forecast(*args, **kwargs).output,
        }

    @abstractmethod
    def _get_current_weather(self, *args, **kwargs) -> dict:
        raise NotImplementedError("_get_current_weather not implemented")

    @abstractmethod
    def _get_forecast(self, *args, **kwargs) -> List[dict]:
        raise NotImplementedError("_get_forecast not implemented")

    def main(self):
        while not self.should_stop():
            try:
                self._status()
            except Exception as e:
                self.logger.exception(e)
            finally:
                self.wait_stop(self.poll_interval)
