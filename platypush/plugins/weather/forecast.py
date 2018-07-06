from platypush.plugins import action
from platypush.plugins.http.request import HttpRequestPlugin


class WeatherForecastPlugin(HttpRequestPlugin):
    """
    Plugin for getting weather updates through Darksky API

    Requires:

        * **requests** (``pip install requests``)
    """

    def __init__(self, darksky_token, lat, long, units='si', **kwargs):
        """
        :param darksky_token: Your token for using the darksky API, see https://darksky.net/dev
        :type darksky_token: str

        :param lat: Default forecast latitude
        :type lat: float

        :param long: Default forecast longitude
        :type long: float

        :param units: Weather units (default: "si").

        Supported units:

            * **si** (international system)
            * **us** (US imperial units)
            * **uk** (UK imperial units)
            * **ca** (Canada imperial units)

        :type units: str
        """

        super().__init__(method='get', output='json')
        self.darksky_token = darksky_token
        self.units = units
        self.lat = lat
        self.long = long
        self.latest_bulletin = {}

    def _get_url(self, lat=None, long=None):
        return 'https://api.darksky.net/forecast/{}/{},{}?units={}'. \
            format(self.darksky_token, (lat or self.lat), (long or self.long),
                   self.units)

    @action
    def get_current_weather(self, lat=None, long=None, **kwargs):
        """
        Get the current weather.

        :param lat: Weather latitude (default: configured latitude)
        :type lat: float

        :param long: Weather longitude (default: configured longitude)
        :type long: float

        :returns: A dictionary containing the current weather object.

        Example output::

                output = {
                    "time": 1529947892,
                    "summary": "Mostly Cloudy",
                    "icon": "partly-cloudy-day",
                    "precipIntensity": 0.0483,
                    "precipProbability": 0.04,
                    "precipType": "rain",
                    "temperature": 27.94,
                    "apparentTemperature": 29.6,
                    "dewPoint": 20.01,
                    "humidity": 0.62,
                    "pressure": 1009.34,
                    "windSpeed": 1.83,
                    "windGust": 5.49,
                    "windBearing": 192,
                    "cloudCover": 0.66,
                    "uvIndex": 0,
                    "visibility": 16.09,
                    "ozone": 273.74
                }
        """

        response = self.get(self._get_url(lat, long))
        return response.output['currently']

    @action
    def get_hourly_forecast(self, lat=None, long=None, **kwargs):
        """
        Get the hourly forecast.

        :param lat: Weather latitude (default: configured latitude)
        :type lat: float

        :param long: Weather longitude (default: configured longitude)
        :type long: float

        :returns: A forecast object.

        Example output::

            output = {
                "summary": "Partly cloudy starting tomorrow morning, continuing until tomorrow evening.",
                "icon": "partly-cloudy-day",
                "data": [
                    {
                        "time": 1529946000,
                        "summary": "Clear",
                        "icon": "clear-day",
                        "precipIntensity": 0,
                        "precipProbability": 0,
                        "temperature": 18.94,
                        "apparentTemperature": 18.94,
                        "dewPoint": 11.99,
                        "humidity": 0.64,
                        "pressure": 1025.53,
                        "windSpeed": 5.1,
                        "windGust": 6.22,
                        "windBearing": 329,
                        "cloudCover": 0.14,
                        "uvIndex": 1,
                        "visibility": 14.19,
                        "ozone": 334.3
                    },
                    {
                        "time": 1529949600,
                        "summary": "Clear",
                        "icon": "clear-day",
                        "precipIntensity": 0,
                        "precipProbability": 0,
                        "temperature": 18.41,
                        "apparentTemperature": 18.41,
                        "dewPoint": 11.12,
                        "humidity": 0.63,
                        "pressure": 1025.54,
                        "windSpeed": 4.6,
                        "windGust": 6.18,
                        "windBearing": 340,
                        "cloudCover": 0.07,
                        "uvIndex": 1,
                        "visibility": 16.09,
                        "ozone": 333.53
                    },
                    # ...
            }
        """

        response = self.get(self._get_url(lat, long))
        return response.output['hourly']

    @action
    def get_daily_forecast(self, lat=None, long=None, **kwargs):
        """
        Get the daily forecast.

        :param lat: Weather latitude (default: configured latitude)
        :type lat: float

        :param long: Weather longitude (default: configured longitude)
        :type long: float

        :returns: A forecast object.

        Example output::

            "output": {
                "summary": "Light rain on Sunday, with high temperatures rising to 28°C on Sunday.",
                "icon": "rain",
                "data": [
                    {
                        "time": 1529877600,
                        "summary": "Mostly cloudy until afternoon.",
                        "icon": "partly-cloudy-day",
                        "sunriseTime": 1529896835,
                        "sunsetTime": 1529957280,
                        "moonPhase": 0.42,
                        "precipIntensity": 0,
                        "precipIntensityMax": 0.0051,
                        "precipIntensityMaxTime": 1529888400,
                        "precipProbability": 0,
                        "temperatureHigh": 20.04,
                        "temperatureHighTime": 1529931600,
                        "temperatureLow": 10.68,
                        "temperatureLowTime": 1529982000,
                        "apparentTemperatureHigh": 20.04,
                        "apparentTemperatureHighTime": 1529931600,
                        "apparentTemperatureLow": 10.68,
                        "apparentTemperatureLowTime": 1529982000,
                        "dewPoint": 12.18,
                        "humidity": 0.77,
                        "pressure": 1025.16,
                        "windSpeed": 3.84,
                        "windGust": 6.51,
                        "windGustTime": 1529881200,
                        "windBearing": 336,
                        "cloudCover": 0.5,
                        "uvIndex": 6,
                        "uvIndexTime": 1529928000,
                        "visibility": 14.08,
                        "ozone": 331.24,
                        "temperatureMin": 13.89,
                        "temperatureMinTime": 1529960400,
                        "temperatureMax": 20.04,
                        "temperatureMaxTime": 1529931600,
                        "apparentTemperatureMin": 13.89,
                        "apparentTemperatureMinTime": 1529960400,
                        "apparentTemperatureMax": 20.04,
                        "apparentTemperatureMaxTime": 1529931600
                    },
                    {
                        "time": 1529964000,
                        "summary": "Partly cloudy throughout the day.",
                        "icon": "partly-cloudy-day",
                        "sunriseTime": 1529983261,
                        "sunsetTime": 1530043677,
                        "moonPhase": 0.45,
                        "precipIntensity": 0,
                        "precipIntensityMax": 0,
                        "precipProbability": 0,
                        "temperatureHigh": 20.95,
                        "temperatureHighTime": 1530018000,
                        "temperatureLow": 11.47,
                        "temperatureLowTime": 1530064800,
                        "apparentTemperatureHigh": 20.95,
                        "apparentTemperatureHighTime": 1530018000,
                        "apparentTemperatureLow": 11.47,
                        "apparentTemperatureLowTime": 1530064800,
                        "dewPoint": 10.19,
                        "humidity": 0.69,
                        "pressure": 1026.14,
                        "windSpeed": 3.67,
                        "windGust": 7.13,
                        "windGustTime": 1530036000,
                        "windBearing": 4,
                        "cloudCover": 0.3,
                        "uvIndex": 5,
                        "uvIndexTime": 1530010800,
                        "visibility": 16.09,
                        "ozone": 328.59,
                        "temperatureMin": 10.68,
                        "temperatureMinTime": 1529982000,
                        "temperatureMax": 20.95,
                        "temperatureMaxTime": 1530018000,
                        "apparentTemperatureMin": 10.68,
                        "apparentTemperatureMinTime": 1529982000,
                        "apparentTemperatureMax": 20.95,
                        "apparentTemperatureMaxTime": 1530018000
                    },
                    # ...
                }
        """

        response = self.get(self._get_url(lat, long))
        return response.output['daily']


# vim:sw=4:ts=4:et:

