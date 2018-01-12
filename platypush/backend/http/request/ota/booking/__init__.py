import datetime
import dateutil.parser
import json

from platypush.backend.http.request import JsonHttpRequest
from platypush.message.event.http.ota.booking import NewReservationEvent


class GetReservationUpdates(JsonHttpRequest):
    """ Gets the reservation updates """
    def __init__(self, hotel_id, token, *args, **kwargs):
        self.hotel_id = hotel_id
        self.token = token
        self.seen_entries = set()
        self.last_update = None

        args = {
            'method': 'get',
            'url': 'https://hub-api.booking.com/v1/hotels/{}/reservations'.format(self.hotel_id),
            'headers': { 'X-Booking-Auth-Token': self.token },
            'params': { 'updatedSince': datetime.date.today().isoformat() }
        }

        super().__init__(args=args, **kwargs)


    def get_new_items(self, response):
        response = response.json()
        entries = []

        for entry in response:
            update_timestamp = dateutil.parser.parse(entry['updateDate'])
            last_update_timestamp = dateutil.parser.parse(self.last_update['updateDate']) \
                if self.last_update else None

            if self.last_update is None \
                    or (update_timestamp > last_update_timestamp
                        and not (
                            entry['booker']['email'] == self.last_update['booker']['email']
                            and entry['status'] == self.last_update['status'])):
                self.last_update = entry
                entries.append(entry)

        return NewReservationEvent(dict(self), entries)


# vim:sw=4:ts=4:et:

