from typing import Optional, Dict, Any

from platypush.plugins import Plugin, action
from platypush.message.response.weather.buienradar import BuienradarWeatherResponse, BuienradarPrecipitationResponse, \
    BuienradarForecastResponse, BuienradarForecast


class WeatherBuienradarPlugin(Plugin):
    """
    Plugin for getting weather updates through Buienradar - a Dutch weather app.

    Requires:

        * **buienradar** (``pip install buienradar``)

    """

    def __init__(self, lat: float, long: float, time_frame: int = 120, **kwargs):
        """
        :param lat: Default latitude
        :param long: Default longitude
        :param time_frame: Default number of minutes to look ahead for precipitation forecast
        """
        super().__init__(**kwargs)
        self.lat = lat
        self.long = long
        self.time_frame = time_frame
        self.latest_bulletin = {}

    def get_data(self, lat: Optional[float] = None, long: Optional[float] = None, time_frame: Optional[int] = None) \
            -> Dict[str, Any]:
        # noinspection PyPackageRequirements
        from buienradar.buienradar import get_data, parse_data
        # noinspection PyPackageRequirements
        from buienradar.constants import SUCCESS, CONTENT, RAINCONTENT, DATA

        lat = lat or self.lat
        long = long or self.long
        time_frame = time_frame or self.time_frame

        result = get_data(latitude=lat, longitude=long)
        if not result.get(SUCCESS):
            raise RuntimeError('Error while retrieving data')

        data = result.get(CONTENT)
        rain_data = result.get(RAINCONTENT)
        result = parse_data(data, rain_data, lat, long, time_frame)
        return result.get(DATA, {})

    @action
    def get_weather(self, lat: Optional[float] = None, long: Optional[float] = None) -> BuienradarWeatherResponse:
        """
        Get the current weather conditions.

        :param lat: Weather latitude (default: configured latitude)
        :param long: Weather longitude (default: configured longitude)
        """
        data = self.get_data(lat, long, 60)

        return BuienradarWeatherResponse(
            barometer_fc=data.get('barometerfcname'),
            condition_name=data.get('condition', {}).get('condition'),
            condition_name_long=data.get('condition', {}).get('exact'),
            condition_image=data.get('condition', {}).get('image'),
            feel_temperature=data.get('feeltemperature'),
            ground_temperature=data.get('groundtemperature'),
            humidity=data.get('humidity'),
            irradiance=data.get('irradiance'),
            measured=data.get('measured'),
            precipitation=data.get('precipitation'),
            pressure=data.get('pressure'),
            rain_last_24_hours=data.get('rainlast24hour'),
            rain_last_hour=data.get('rainlasthour'),
            station_name=data.get('stationname'),
            temperature=data.get('temperature'),
            visibility=data.get('visibility'),
            wind_azimuth=data.get('windazimuth'),
            wind_direction=data.get('wind_irection'),
            wind_force=data.get('windforce'),
            wind_gust=data.get('windgust'),
            wind_speed=data.get('windspeed')
        )

    @action
    def get_forecast(self, lat: Optional[float] = None, long: Optional[float] = None) -> BuienradarForecastResponse:
        """
        Get the weather forecast for the next days.

        :param lat: Weather latitude (default: configured latitude)
        :param long: Weather longitude (default: configured longitude)
        """
        data = self.get_data(lat, long, 60).get('forecast', [])
        return BuienradarForecastResponse([
            BuienradarForecast(
                condition_name=d.get('condition', {}).get('condition'),
                condition_name_long=d.get('condition', {}).get('exact'),
                condition_image=d.get('condition', {}).get('image'),
                date_time=d.get('datetime'),
                rain=d.get('rain'),
                min_rain=d.get('minrain'),
                max_rain=d.get('maxrain'),
                rain_chance=d.get('rainchance'),
                snow=d.get('snow'),
                temperature=d.get('temperature'),
                wind_azimuth=d.get('windazimuth'),
                wind_direction=d.get('winddirection'),
                wind_force=d.get('windforce'),
                wind_speed=d.get('windspeed'),
            )
            for d in data
        ])

    @action
    def get_precipitation(self, lat: Optional[float] = None, long: Optional[float] = None,
                          time_frame: Optional[int] = None) -> BuienradarPrecipitationResponse:
        """
        Get the precipitation forecast for the specified time frame.

        :param lat: Weather latitude (default: configured latitude)
        :param long: Weather longitude (default: configured longitude)
        :param time_frame: Time frame for the forecast in minutes (default: configured time_frame)
        """
        data = self.get_data(lat, long, time_frame).get('precipitation_forecast', {})
        return BuienradarPrecipitationResponse(
            average=data.get('average'),
            total=data.get('total'),
            time_frame=data.get('timeframe'),
        )


# vim:sw=4:ts=4:et:
