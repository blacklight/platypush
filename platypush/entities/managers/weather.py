from abc import ABC, abstractmethod
from typing import List

from platypush.utils import get_plugin_name_by_class

from . import EntityManager


class WeatherEntityManager(EntityManager, ABC):
    """
    Base class for integrations that support weather reports.
    """

    def transform_entities(self, entities: List[dict]):
        from platypush.entities.weather import Weather

        if not entities:
            return []

        weather = entities[0]
        plugin = get_plugin_name_by_class(self.__class__)
        return super().transform_entities(
            [
                Weather(
                    id=plugin,
                    name='Weather',
                    summary=weather.get('summary'),
                    icon=weather.get('icon'),
                    image=weather.get('image'),
                    precip_intensity=weather.get('precip_intensity'),
                    precip_type=weather.get('precip_type'),
                    temperature=weather.get('temperature'),
                    apparent_temperature=weather.get('apparent_temperature'),
                    humidity=weather.get('humidity'),
                    pressure=weather.get('pressure'),
                    rain_chance=weather.get('rain_chance'),
                    wind_speed=weather.get('wind_speed'),
                    wind_direction=weather.get('wind_direction'),
                    wind_gust=weather.get('wind_gust'),
                    cloud_cover=weather.get('cloud_cover'),
                    visibility=weather.get('visibility'),
                    sunrise=weather.get('sunrise'),
                    sunset=weather.get('sunset'),
                    units=weather.get('units'),
                )
            ]
        )

    @abstractmethod
    def status(self, *_, **__):
        raise NotImplementedError
