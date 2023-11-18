from typing import Optional
from marshmallow import fields, pre_dump
from marshmallow.schema import Schema

from platypush.schemas import DateTime


def _get_precip_type(response: dict) -> Optional[str]:
    if response.get('snow', {}).get('1h', 0) > 0:
        return 'snow'
    if response.get('rain', {}).get('1h', 0) > 0:
        return 'rain'
    return None


class WeatherSchema(Schema):
    """
    Schema for weather data.
    """

    summary = fields.Function(
        lambda obj: obj.get('weather', [{'main': 'Unknown'}])[0].get('main', 'Unknown'),
        metadata={
            'description': 'Summary of the weather condition',
            'example': 'Cloudy',
        },
    )

    icon = fields.Function(
        lambda obj: obj.get('weather', [{'icon': 'unknown'}])[0].get('icon', 'unknown'),
        metadata={
            'description': 'Icon representing the weather condition',
            'example': 'cloudy',
        },
    )

    precip_intensity = fields.Function(
        lambda obj: obj.get('rain', obj.get('snow', {})).get('1h', 0),
        metadata={
            'description': 'Intensity of the precipitation',
            'example': 0.0,
        },
    )

    precip_type = fields.Function(
        _get_precip_type,
        metadata={
            'description': 'Type of precipitation',
            'example': 'rain',
        },
    )

    temperature = fields.Function(
        lambda obj: obj.get('main', {}).get('temp'),
        metadata={
            'description': 'Temperature in the configured unit of measure',
            'example': 10.0,
        },
    )

    apparent_temperature = fields.Function(
        lambda obj: obj.get('main', {}).get('feels_like'),
        metadata={
            'description': 'Apparent temperature in the configured unit of measure',
            'example': 9.0,
        },
    )

    humidity = fields.Function(
        lambda obj: obj.get('main', {}).get('humidity'),
        metadata={
            'description': 'Humidity percentage, between 0 and 100',
            'example': 30,
        },
    )

    pressure = fields.Function(
        lambda obj: obj.get('main', {}).get('pressure'),
        metadata={
            'description': 'Pressure in hPa',
            'example': 1000.0,
        },
    )

    wind_speed = fields.Function(
        lambda obj: obj.get('wind', {}).get('speed'),
        metadata={
            'description': 'Wind speed in the configured unit of measure',
            'example': 10.0,
        },
    )

    wind_direction = fields.Function(
        lambda obj: obj.get('wind', {}).get('deg'),
        metadata={
            'description': 'Wind direction in degrees',
            'example': 180.0,
        },
    )

    wind_gust = fields.Function(
        lambda obj: obj.get('wind', {}).get('gust'),
        metadata={
            'description': 'Wind gust in the configured unit of measure',
            'example': 15.0,
        },
    )

    cloud_cover = fields.Function(
        lambda obj: obj.get('clouds', {}).get('all'),
        metadata={
            'description': 'Cloud cover percentage between 0 and 100',
            'example': 0.5,
        },
    )

    visibility = fields.Float(
        metadata={
            'description': 'Visibility in meters',
            'example': 2000.0,
        },
    )

    sunrise = DateTime(
        metadata={
            'description': 'Sunrise time',
            'example': '2020-01-01T06:00:00+00:00',
        },
    )

    sunset = DateTime(
        metadata={
            'description': 'Sunset time',
            'example': '2020-01-01T18:00:00+00:00',
        },
    )

    @pre_dump
    def _pre_dump(self, data: dict, **_) -> dict:
        sun_data = data.pop('sys', {})
        sunrise = sun_data.get('sunrise')
        sunset = sun_data.get('sunset')

        if sunrise is not None:
            data['sunrise'] = sunrise
        if sunset is not None:
            data['sunset'] = sunset

        return data
