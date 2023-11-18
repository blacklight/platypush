from datetime import datetime
from typing import Optional

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
        precip_intensity: Optional[float] = None,
        precip_type: Optional[str] = None,
        temperature: Optional[float] = None,
        apparent_temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        pressure: Optional[float] = None,
        wind_speed: Optional[float] = None,
        wind_gust: Optional[float] = None,
        wind_direction: Optional[float] = None,
        cloud_cover: Optional[float] = None,
        visibility: Optional[float] = None,
        sunrise: Optional[datetime] = None,
        sunset: Optional[datetime] = None,
        **kwargs,
    ):
        """
        :param plugin_name: Plugin that triggered the event.
        :param summary: Summary of the weather condition.
        :param icon: Icon representing the weather condition.
        :param precip_intensity: Intensity of the precipitation.
        :param precip_type: Type of precipitation.
        :param temperature: Temperature, in the configured unit system.
        :param apparent_temperature: Apparent temperature, in the configured
            unit system.
        :param humidity: Humidity percentage, between 0 and 100.
        :param pressure: Pressure, in the configured unit system.
        :param wind_speed: Wind speed, in the configured unit system.
        :param wind_gust: Wind gust, in the configured unit system.
        :param wind_direction: Wind direction, in degrees.
        :param cloud_cover: Cloud cover percentage, between 0 and 100.
        :param visibility: Visibility, in meters.
        :param sunrise: Sunrise time.
        :param sunset: Sunset time.
        """
        super().__init__(
            *args,
            plugin_name=plugin_name,
            summary=summary,
            icon=icon,
            precip_intensity=precip_intensity,
            precip_type=precip_type,
            temperature=temperature,
            apparent_temperature=apparent_temperature,
            humidity=humidity,
            pressure=pressure,
            wind_speed=wind_speed,
            wind_gust=wind_gust,
            wind_direction=wind_direction,
            cloud_cover=cloud_cover,
            visibility=visibility,
            sunrise=sunrise,
            sunset=sunset,
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


# vim:sw=4:ts=4:et:
