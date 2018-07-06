import datetime
import dateutil.parser

from platypush.plugins import action
from platypush.plugins.http.request import HttpRequestPlugin

class HttpRequestOtaBookingPlugin(HttpRequestPlugin):
    """ Plugin to send requests to the Booking Hub API """

    def __init__(self, hotel_id, token, timeout=5, **kwargs):
        self.hotel_id = hotel_id
        self.token = token
        self.timeout = timeout


    @action
    def get_reservations(self, day='today'):
        url = 'https://hub-api.booking.com/v1/hotels/{}/reservations' \
            .format(self.hotel_id)

        today = datetime.date.today().isoformat()
        if day == 'today': day = today

        headers = { 'X-Booking-Auth-Token': self.token }
        params = { 'checkin': day }

        response = self.get(url, headers=headers, params=params,
                            output='json', timeout=self.timeout)

        reservations = [res for res in response.output
                        if res['status'] != 'CANCELLED']

        response.output = {
            'reservations': reservations,
            'n_reservations': len(reservations),
        }

        return response


# vim:sw=4:ts=4:et:

