from abc import ABC, abstractmethod
from typing import List

from platypush.utils import get_plugin_name_by_class

from . import EntityManager


class WeatherEntityManager(EntityManager, ABC):
    """
    Base class for integrations that support weather reports.
    """

    def transform_entities(self, entities: List[dict], *, type: str):
        from platypush.entities.weather import Weather, WeatherForecast

        if not entities:
            return []

        plugin = get_plugin_name_by_class(self.__class__)

        if type == 'weather':
            # Current weather response
            weather = entities[0]
            weather.pop('time', None)
            return super().transform_entities(
                [
                    Weather(
                        id=f'{plugin}:weather',
                        name='Weather',
                        **weather,
                    )
                ]
            )

        # Weather forecast response
        if type == 'forecast':
            return super().transform_entities(
                [
                    WeatherForecast(
                        id=f'{plugin}:forecast',
                        name='Forecast',
                        forecast=entities,
                    )
                ]
            )

        raise AssertionError(f'Unexpected weather entity type: {type}')

    @abstractmethod
    def status(self, *_, **__):
        raise NotImplementedError
