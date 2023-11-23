from datetime import datetime
from typing import List, Optional

from platypush.message.event import Event


class NewWeatherConditionEvent(Event):
    """
    Event triggered when the weather condition changes
    """

    def __init__(
        self,
        *args,
        plugin_name: str,
        summary: Optional[str] = None,
        icon: Optional[str] = None,
        image: Optional[str] = None,
        precip_intensity: Optional[float] = None,
        precip_type: Optional[str] = None,
        temperature: Optional[float] = None,
        apparent_temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        pressure: Optional[float] = None,
        rain_chance: Optional[float] = None,
        wind_speed: Optional[float] = None,
        wind_gust: Optional[float] = None,
        wind_direction: Optional[float] = None,
        cloud_cover: Optional[float] = None,
        visibility: Optional[float] = None,
        sunrise: Optional[datetime] = None,
        sunset: Optional[datetime] = None,
        units: str = 'metric',
        **kwargs,
    ):
        """
        :param plugin_name: Plugin that triggered the event.
        :param summary: Summary of the weather condition.
        :param icon: Icon representing the weather condition.
        :param image: Image URL representing the weather condition.
        :param precip_intensity: Intensity of the precipitation.
        :param precip_type: Type of precipitation.
        :param temperature: Temperature, in the configured unit system.
        :param apparent_temperature: Apparent temperature, in the configured
            unit system.
        :param humidity: Humidity percentage, between 0 and 100.
        :param pressure: Pressure, in the configured unit system.
        :param rain_chance: Chance of rain, between 0 and 100.
        :param wind_speed: Wind speed, in the configured unit system.
        :param wind_gust: Wind gust, in the configured unit system.
        :param wind_direction: Wind direction, in degrees.
        :param cloud_cover: Cloud cover percentage, between 0 and 100.
        :param visibility: Visibility, in meters.
        :param sunrise: Sunrise time.
        :param sunset: Sunset time.
        :param units: Unit system (default: metric).
        """
        super().__init__(
            *args,
            plugin_name=plugin_name,
            summary=summary,
            icon=icon,
            image=image,
            precip_intensity=precip_intensity,
            precip_type=precip_type,
            temperature=temperature,
            apparent_temperature=apparent_temperature,
            humidity=humidity,
            pressure=pressure,
            rain_chance=rain_chance,
            wind_speed=wind_speed,
            wind_gust=wind_gust,
            wind_direction=wind_direction,
            cloud_cover=cloud_cover,
            visibility=visibility,
            sunrise=sunrise,
            sunset=sunset,
            units=units,
            **kwargs,
        )


class NewPrecipitationForecastEvent(Event):
    """
    Event triggered when the precipitation forecast changes
    """

    def __init__(
        self,
        *args,
        plugin_name: Optional[str] = None,
        average: float,
        total: float,
        time_frame: int,
        **kwargs,
    ):
        super().__init__(
            *args,
            plugin_name=plugin_name,
            average=average,
            total=total,
            time_frame=time_frame,
            **kwargs,
        )


class NewWeatherForecastEvent(Event):
    """
    Event triggered when a new weather forecast is received.
    """

    def __init__(
        self,
        *args,
        plugin_name: str,
        forecast: List[dict],
        **kwargs,
    ):
        """
        :param forecast: List of weather forecast items. Format:

            .. schema:: weather.openweathermap.WeatherSchema(many=True)

        """
        super().__init__(
            *args,
            plugin_name=plugin_name,
            forecast=forecast,
            **kwargs,
        )


# vim:sw=4:ts=4:et:
