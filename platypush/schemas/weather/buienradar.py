from marshmallow import EXCLUDE, fields
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class WeatherSchema(Schema):
    """
    Schema for weather data.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Weather schema metadata.
        """

        unknown = EXCLUDE

    time = DateTime(
        required=True,
        attribute='datetime',
        metadata={
            'description': 'Date and time of the weather data',
            'example': '2020-01-01T00:00:00+00:00',
        },
    )

    summary = fields.Function(
        lambda obj: obj.get('condition', {}).get('exact', 'Unknown'),
        metadata={
            'description': 'Summary of the weather condition',
            'example': 'Cloudy',
        },
    )

    image = fields.Function(
        lambda obj: obj.get('condition', {}).get('image'),
        metadata={
            'description': 'Image URL representing the weather condition',
            'example': 'https://www.buienradar.nl/resources/images/icons/weather/30x30/cc.png',
        },
    )

    precip_intensity = fields.Float(
        attribute='rainlasthour',
        metadata={
            'description': 'Amount of precipitation in the last hour in mm/h',
            'example': 0.0,
        },
    )

    precip_type = fields.Function(
        lambda obj: 'snow' if obj.get('snow') else 'rain',
        metadata={
            'description': 'Type of precipitation',
            'example': 'rain',
        },
    )

    temperature = fields.Float(
        metadata={
            'description': 'Temperature in Celsius',
            'example': 10.0,
        },
    )

    apparent_temperature = fields.Float(
        attribute='feeltemperature',
        metadata={
            'description': 'Apparent temperature in Celsius',
            'example': 9.0,
        },
    )

    humidity = fields.Float(
        metadata={
            'description': 'Humidity percentage, between 0 and 100',
            'example': 30,
        },
    )

    pressure = fields.Float(
        metadata={
            'description': 'Pressure in hPa',
            'example': 1000.0,
        },
    )

    rain_chance = fields.Float(
        attribute='rainchance',
        metadata={
            'description': 'Chance of rain in percentage, between 0 and 100',
            'example': 30,
        },
    )

    wind_speed = fields.Float(
        attribute='windspeed',
        metadata={
            'description': 'Wind speed in the configured unit of measure',
            'example': 10.0,
        },
    )

    wind_direction = fields.Float(
        attribute='windazimuth',
        metadata={
            'description': 'Wind direction in degrees',
            'example': 180,
        },
    )

    wind_gust = fields.Float(
        attribute='windgust',
        metadata={
            'description': 'Wind gust in the configured unit of measure',
            'example': 15.0,
        },
    )

    visibility = fields.Float(
        metadata={
            'description': 'Visibility in meters',
            'example': 2000.0,
        },
    )

    units = fields.Constant(
        'metric',
        metadata={
            'description': 'Unit of measure',
            'example': 'metric',
        },
    )


class PrecipitationForecastSchema(Schema):
    """
    Schema for precipitation forecast data.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Precipitation forecast schema metadata.
        """

        unknown = EXCLUDE

    timeframe = fields.Integer(
        metadata={
            'description': 'Time frame in minutes',
            'example': 60,
        },
    )

    total = fields.Float(
        metadata={
            'description': 'Total precipitation in mm/h',
            'example': 0.5,
        },
    )

    average = fields.Float(
        metadata={
            'description': 'Average precipitation in mm/h',
            'example': 0.25,
        },
    )
