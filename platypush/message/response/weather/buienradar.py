import datetime

from typing import List

from platypush.message import Mapping
from platypush.message.response import Response


class BuienradarWeatherResponse(Response):
    def __init__(self,
                 barometer_fc: str,
                 condition_name: str,
                 condition_name_long: str,
                 condition_image: str,
                 feel_temperature: float,
                 ground_temperature: float,
                 humidity: int,
                 irradiance: int,
                 measured: datetime.datetime,
                 precipitation: float,
                 pressure: float,
                 rain_last_24_hours: float,
                 rain_last_hour: float,
                 station_name: str,
                 temperature: float,
                 visibility: int,
                 wind_azimuth: int,
                 wind_direction: str,
                 wind_force: int,
                 wind_gust: float,
                 wind_speed: float,
                 *args, **kwargs):
        super().__init__(*args, output={
            'barometer_fc': barometer_fc,
            'condition_name': condition_name,
            'condition_name_long': condition_name_long,
            'condition_image': condition_image,
            'feel_temperature': feel_temperature,
            'ground_temperature': ground_temperature,
            'humidity': humidity,
            'irradiance': irradiance,
            'measured': measured,
            'precipitation': precipitation,
            'pressure': pressure,
            'rain_last_24_hours': rain_last_24_hours,
            'rain_last_hour': rain_last_hour,
            'station_name': station_name,
            'temperature': temperature,
            'visibility': visibility,
            'wind_azimuth': wind_azimuth,
            'wind_direction': wind_direction,
            'wind_force': wind_force,
            'wind_gust': wind_gust,
            'wind_speed': wind_speed,
        }, **kwargs)


class BuienradarPrecipitationResponse(Response):
    def __init__(self,
                 average: float,
                 total: float,
                 time_frame: int,
                 *args, **kwargs):
        super().__init__(*args, output={
            'average': average,
            'total': total,
            'time_frame': time_frame,
        }, **kwargs)


class BuienradarForecast(Mapping):
    def __init__(self,
                 condition_name: str,
                 condition_name_long: str,
                 condition_image: str,
                 date_time: datetime.datetime,
                 rain: float,
                 min_rain: float,
                 max_rain: float,
                 rain_chance: float,
                 snow: int,
                 temperature: float,
                 wind_azimuth: int,
                 wind_direction: str,
                 wind_force: int,
                 wind_speed: float,
                 *args, **kwargs):
        super().__init__(*args, output={
            'condition_name': condition_name,
            'condition_name_long': condition_name_long,
            'condition_image': condition_image,
            'date_time': date_time,
            'rain': rain,
            'min_rain': min_rain,
            'max_rain': max_rain,
            'rain_chance': rain_chance,
            'snow': snow,
            'temperature': temperature,
            'wind_azimuth': wind_azimuth,
            'wind_direction': wind_direction,
            'wind_force': wind_force,
            'wind_speed': wind_speed,
        }, **kwargs)


class BuienradarForecastResponse(Response):
    def __init__(self,
                 forecast=List[BuienradarForecast],
                 *args, **kwargs):
        super().__init__(*args, output=forecast, **kwargs)


# vim:sw=4:ts=4:et:
