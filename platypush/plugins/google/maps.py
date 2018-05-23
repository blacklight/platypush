import json
import logging
import requests

from platypush.message.response import Response
from platypush.plugins.google import GooglePlugin


class GoogleMapsPlugin(GooglePlugin):
    scopes = []

    def __init__(self, api_key, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)
        self.api_key = api_key


    def get_address_from_latlng(self, latitude, longitude):
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                                params = {
                                    'latlng': '{},{}'.format(latitude, longitude),
                                    'key': self.api_key,
                                }).json()

        address = dict(
            (t, None) for t in ['street_number', 'street', 'locality', 'country', 'postal_code']
        )

        address['latitude'] = latitude
        address['longitude'] = longitude

        if 'results' in response and response['results']:
            result = response['results'][0]
            logging.info('Google Maps geocode response for latlng ({},{}): {}'.
                         format(latitude, longitude, result))

            address['address'] = result['formatted_address'].split(',')[0]
            for addr_component in result['address_components']:
                for component_type in addr_component['types']:
                    if component_type == 'locality':
                        address['locality'] = addr_component['long_name']
                    elif component_type == 'country':
                        address['country'] = addr_component['short_name'].lower()
                    elif component_type == 'postal_code':
                        address['postal_code'] = addr_component['long_name']

        return Response(output=address)


# vim:sw=4:ts=4:et:

