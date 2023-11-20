from abc import ABC, abstractmethod
from typing import Optional
from platypush.entities.managers.weather import WeatherEntityManager

from platypush.message.event.weather import NewWeatherConditionEvent
from platypush.plugins import RunnablePlugin, action
from platypush.utils import get_plugin_name_by_class


class WeatherPlugin(RunnablePlugin, WeatherEntityManager, ABC):
    """
    Base class for weather plugins.
    """

    def __init__(self, poll_interval: Optional[float] = 120, **kwargs):
        super().__init__(poll_interval=poll_interval, **kwargs)
        self._latest_weather = None

    def _on_weather_data(self, weather: dict, always_publish: bool = False):
        if weather != self._latest_weather or always_publish:
            self._bus.post(
                NewWeatherConditionEvent(
                    plugin_name=get_plugin_name_by_class(self.__class__), **weather
                )
            )

            self.publish_entities([weather])

        self._latest_weather = weather

    @action
    def get_current_weather(self, *args, **kwargs) -> dict:
        weather = self._get_current_weather(*args, **kwargs)
        self._on_weather_data(weather, always_publish=True)
        return weather

    @action
    def status(self, *args, **kwargs):
        """
        Alias for :meth:`get_current_weather`.
        """
        return self.get_current_weather(*args, **kwargs)

    @abstractmethod
    def _get_current_weather(self, *args, **kwargs) -> dict:
        raise NotImplementedError("_get_current_weather not implemented")

    def main(self):
        while not self.should_stop():
            try:
                current_weather = self._get_current_weather() or {}
                current_weather.pop("time", None)

                if current_weather != self._latest_weather:
                    self._bus.post(
                        NewWeatherConditionEvent(
                            plugin_name=get_plugin_name_by_class(self.__class__),
                            **current_weather
                        )
                    )

                self._latest_weather = current_weather
            except Exception as e:
                self.logger.exception(e)
            finally:
                self.wait_stop(self.poll_interval)
