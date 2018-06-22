from platypush.message.response import Response
from platypush.plugins.http.request import HttpRequestPlugin


class WeatherForecastPlugin(HttpRequestPlugin):
    """ Plugin for getting weather updates through Darksky API """

    def __init__(self, darksky_token, lat, long, units='si', **kwargs):
        """ Supported unit types: ca, uk2, us, si """

        super().__init__(method='get', output='json')
        self.latest_bulletin = {}
        self.url = 'https://api.darksky.net/forecast/{}/{},{}?units={}'. \
            format(darksky_token, lat, long, units)

    def get_current_weather(self, **kwargs):
        response = self.get(self.url)
        print(response)
        return Response(output=response.output['currently'])

    def get_hourly_forecast(self, **kwargs):
        response = self.get(self.url)
        return Response(output=response.output['hourly'])

    def get_daily_forecast(self, **kwargs):
        response = self.get(self.url)
        return Response(output=response.output['daily'])


# vim:sw=4:ts=4:et:

