"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from datetime import datetime
from typing import List, Union, Optional

import requests

from platypush.plugins import action
from platypush.plugins.google import GooglePlugin
from platypush.schemas.maps import MapsTravelTimeSchema
from platypush.utils import to_datetime

datetime_types = Union[str, int, float, datetime]


class GoogleMapsPlugin(GooglePlugin):
    """
    Plugins that provides utilities to interact with Google Maps API services.

    Requires:

        * **google-api-python-client** (``pip install google-api-python-client``)
        * **oauth2client** (``pip install oauth2client``)

    """

    scopes = []

    def __init__(self, api_key, *args, **kwargs):
        """
        :param api_key: Server-side API key to be used for the requests, get one at
            https://console.developers.google.com
        :type api_key: str
        """

        super().__init__(scopes=self.scopes, *args, **kwargs)
        self.api_key = api_key

    @action
    def get_address_from_latlng(self, latitude, longitude):
        """
        Get an address information given lat/long

        :param latitude: Latitude
        :type latitude: float

        :param longitude: Longitude
        :type longitude: float
        """

        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                                params={
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
            self.logger.info('Google Maps geocode response for latlng ({},{}): {}'.
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

        return address

    @action
    def get_elevation_from_latlng(self, latitude, longitude):
        """
        Get the elevation in meters of a geo point given lat/long

        :param latitude: Latitude
        :type latitude: float

        :param longitude: Longitude
        :type longitude: float
        """

        response = requests.get('https://maps.googleapis.com/maps/api/elevation/json',
                                params={
                                    'locations': '{},{}'.format(latitude, longitude),
                                    'key': self.api_key,
                                }).json()

        elevation = None

        if response.get('results'):
            elevation = response['results'][0]['elevation']

        return {'elevation': elevation}

    @action
    def get_travel_time(self, origins: List[str], destinations: List[str],
                        departure_time: Optional[datetime_types] = None,
                        arrival_time: Optional[datetime_types] = None,
                        units: str = 'metric',
                        avoid: Optional[List[str]] = None,
                        language: Optional[str] = None,
                        mode: Optional[str] = None,
                        traffic_model: Optional[str] = None,
                        transit_mode: Optional[List[str]] = None,
                        transit_route_preference: Optional[str] = None):
        """
        Get the estimated travel time between a set of departure points and a set of destinations.

        :param origins: The starting point(s) for calculating travel distance and time. Locations are supplied in the
            form of a place ID, an address, or latitude/longitude coordinates:

            * *Place ID*: If you supply a place ID, you must prefix it with ``place_id:``.
            * *Address*: If you pass an address, the service geocodes the string and converts it to a
              latitude/longitude coordinate to calculate distance.
            * *Coordinates*: If you pass latitude/longitude coordinates, they they will snap to the nearest road.

        :param destinations: The arrival point(s) for calculating travel distance and time. Locations are supplied in
            the form of a place ID, an address, or latitude/longitude coordinates:

            * *Place ID*: If you supply a place ID, you must prefix it with ``place_id:``.
            * *Address*: If you pass an address, the service geocodes the string and converts it to a
              latitude/longitude coordinate to calculate distance.
            * *Coordinates*: If you pass latitude/longitude coordinates, they they will snap to the nearest road.

        :param departure_time: Preferred departure time, as a UNIX timestamp, an ISO8601 string or a datetime object.
        :param arrival_time: Preferred arrival time, as a UNIX timestamp, an ISO8601 string or a datetime object.
        :param units: ``metric`` (default) or ``imperial``.
        :param avoid: Any of the following values:

            * ``tolls``: indicates that the calculated route should avoid toll roads/bridges.
            * ``highways``: indicates that the calculated route should avoid highways.
            * ``ferries``: indicates that the calculated route should avoid ferries.
            * ``indoor`` indicates that the calculated route should avoid indoor steps for walking and transit
              directions.

        :param language: Target language for the results (ISO string). If none is specified then the target language
            is inferred from the ``Accept-Language`` header or the preferred language associated to the account.
        :param mode: Any of the following:

            * ``DRIVING`` (default)
            * ``WALKING``
            * ``BICYCLING``
            * ``TRANSIT``

        :param traffic_model: Specifies the assumptions to use when calculating time in traffic. This setting affects
            the value returned in the ``duration_in_traffic`` field in the response, which contains the predicted time
            in traffic based on historical averages. Available values:

                * ``best_guess`` (default) indicates that the returned ``duration_in_traffic`` should be the best
                    estimate of travel time given what is known about both historical traffic conditions and live
                    traffic. Live traffic becomes more important the closer the departure_time is to now.
                * ``pessimistic`` indicates that the returned ``duration_in_traffic`` should be longer than the actual
                  travel time on most days, though occasional days with particularly bad traffic conditions may exceed
                  this value.
                * ``optimistic`` indicates that the returned ``duration_in_traffic`` should be shorter than the actual
                  travel time on most days, though occasional days with particularly good traffic conditions may be
                  faster than this value.

        :param transit_mode:  Specifies one or more preferred modes of transit. This parameter may only be specified
            for transit directions. Available values:

                * ``bus`` indicates that the calculated route should prefer travel by bus.
                * ``subway`` indicates that the calculated route should prefer travel by subway.
                * ``train`` indicates that the calculated route should prefer travel by train.
                * ``tram`` indicates that the calculated route should prefer travel by tram and light rail.
                * ``rail`` indicates that the calculated route should prefer travel by train, tram, light rail, and
                   subway. This is equivalent to ``transit_mode=["train", "tram", "subway"]``.

        :param transit_route_preference: Specifies preferences for transit routes. Using this parameter, you can
            bias the options returned, rather than accepting the default best route chosen by the API. This parameter
            may only be specified for transit directions. Available values:

                - ``less_walking`` indicates that the calculated route should prefer limited amounts of walking.
                - ``fewer_transfers`` indicates that the calculated route should prefer a limited number of transfers.

        :return: .. schema:: maps.MapsTravelTimeSchema
        """
        rs = requests.get(
            'https://maps.googleapis.com/maps/api/distancematrix/json',
            params={
                'origins': '|'.join(origins),
                'destinations': '|'.join(destinations),
                'units': units,
                **({'departure_time': to_datetime(departure_time)} if departure_time else {}),
                **({'arrival_time': to_datetime(arrival_time)} if arrival_time else {}),
                **({'avoid': '|'.join(avoid)} if avoid else {}),
                **({'language': language} if language else {}),
                **({'mode': mode} if mode else {}),
                **({'traffic_model': traffic_model} if traffic_model else {}),
                **({'transit_mode': transit_mode} if transit_mode else {}),
                **({'transit_route_preference': transit_route_preference}
                   if transit_route_preference else {}),
                'key': self.api_key,
            }).json()

        assert not rs.get('error_message'), f'{rs["status"]}: {rs["error_message"]}'
        rows = rs.get('rows', [])
        assert rows, 'The API returned no rows'
        elements = rows[0].get('elements')
        assert elements, 'The API returned no elements'

        return MapsTravelTimeSchema().dump(elements, many=True)


# vim:sw=4:ts=4:et:
