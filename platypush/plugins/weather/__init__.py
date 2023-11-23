from abc import ABC, abstractmethod
from typing import List, Optional
from platypush.entities.managers.weather import WeatherEntityManager

from platypush.message.event.weather import (
    NewWeatherConditionEvent,
    NewWeatherForecastEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.weather.openweathermap import WeatherReportSchema
from platypush.utils import get_plugin_name_by_class


class WeatherPlugin(RunnablePlugin, WeatherEntityManager, ABC):
    """
    Base class for weather plugins.
    """

    def __init__(self, poll_interval: Optional[float] = 120, **kwargs):
        super().__init__(poll_interval=poll_interval, **kwargs)
        self._latest_weather = None
        self._latest_forecast = None

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
        **kwargs
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
        **kwargs
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
    def status(self, *args, **kwargs) -> dict:
        """
        :return: .. schema:: weather.openweathermap.WeatherReportSchema
        """
        return self._status(*args, **kwargs)

    def _status(self, *args, **kwargs) -> dict:
        return dict(
            WeatherReportSchema().dump(
                {
                    'current': self.get_current_weather(*args, **kwargs).output,
                    'forecast': self.get_forecast(*args, **kwargs).output,
                }
            )
        )

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
