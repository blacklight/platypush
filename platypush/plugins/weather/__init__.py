from abc import ABC, abstractmethod
from typing import Optional

from platypush.message.event.weather import NewWeatherConditionEvent
from platypush.plugins import RunnablePlugin, action
from platypush.utils import get_plugin_name_by_class


class WeatherPlugin(RunnablePlugin, ABC):
    """
    Base class for weather plugins.
    """

    def __init__(self, poll_interval: Optional[float] = 120, **kwargs):
        super().__init__(poll_interval=poll_interval, **kwargs)
        self._latest_weather = None

    @action
    @abstractmethod
    def get_current_weather(self, *args, **kwargs):
        raise NotImplementedError("get_current_weather not implemented")

    def main(self):
        while not self.should_stop():
            try:
                current_weather = dict(self.get_current_weather().output or {})  # type: ignore
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
