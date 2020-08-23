import datetime
import requests
from typing import List, Dict, Any, Optional, Union, Tuple

from platypush.plugins import Plugin, action


class FoursquarePlugin(Plugin):
    """
    Plugin to interact with the `Foursquare Places API <https://developer.foursquare.com/docs/api>`_.

    In order to enable the Foursquare API on your account you need to:

        - Create a new app on the `Foursquare developers website <https://foursquare.com/developers/signup>`_.
        - Copy the ``client_id`` and ``client_secret``.
        - Add a redirect URL. It must point to a valid IP/hostname with a web server running, even if it runs
            locally. You can also use the local URL of the platypush web server - e.g. http://192.168.1.2:8008/.
        - Open the following URL: ``https://foursquare.com/oauth2/authenticate?client_id=CLIENT_ID&response_type=token&redirect_uri=REDIRECT_URI``.
            Replace ``CLIENT_ID`` and ``REDIRECT_URI`` with the parameters from your app.
        - Allow the application. You will be redirected to the URL you provided. Copy the ``access_token`` provided in
            the URL.

    """

    api_base_url = 'https://api.foursquare.com/v2'

    def __init__(self, access_token: str, **kwargs):
        """
        :param access_token:
        """
        super().__init__(**kwargs)
        self.access_token = access_token

    def _get_url(self, endpoint):
        return '{url}/{endpoint}?oauth_token={token}&v={version}'.format(
            url=self.api_base_url, endpoint=endpoint, token=self.access_token,
            version=datetime.date.today().strftime('%Y%m%d'),
        )

    @action
    def get_checkins(self) -> List[Dict[str, Any]]:
        """
        Get the list of check-ins of the current user.
        :return: A list of checkins, as returned by the Foursquare API.
        """
        url = self._get_url('users/self/checkins')
        return requests.get(url).json().get('response', {}).get('checkins', {}).get('items', [])

    # noinspection DuplicatedCode
    @action
    def search(self,
               latitude: Optional[float] = None,
               longitude: Optional[float] = None,
               altitude: Optional[float] = None,
               latlng_accuracy: Optional[float] = None,
               altitude_accuracy: Optional[float] = None,
               near: Optional[str] = None,
               query: Optional[str] = None,
               limit: Optional[int] = None,
               url: Optional[int] = None,
               categories: Optional[List[str]] = None,
               radius: Optional[int] = None,
               sw: Optional[Union[Tuple[float], List[float]]] = None,
               ne: Optional[Union[Tuple[float], List[float]]] = None,) -> List[Dict[str, Any]]:
        """
        Search for venues.

        :param latitude: Search near this latitude. Note either ``latitude, longitude`` or ``near`` should be provided.
        :param longitude: Search near this latitude. Note either ``latitude, longitude`` or ``near`` should be provided.
        :param near: Search near this place (e.g. "Chicago, IL" or "Amsterdam, NL"). Note either
            ``latitude, longitude`` or ``near`` should be provided.
        :param altitude: Search near this altitude in meters.
        :param latlng_accuracy:  Latitude/longitude accuracy in meters.
        :param altitude_accuracy: Altitude accuracy in meters.
        :param query: Search query (e.g. "coffee shops" or "restaurants").
        :param limit: Maximum number of results.
        :param url: Venue URL to search.
        :param categories: List of `category IDs <https://developer.foursquare.com/docs/resources/categories>`_
            to be searched.
        :param radius: Search radius in meters.
        :param sw: South/west boundary box as a ``[latitude, longitude]`` pair.
        :param ne: North/east boundary box as a ``[latitude, longitude]`` pair.
        :return: A list of venues, as returned by the Foursquare API.
        """
        assert (latitude and longitude) or near, 'Specify either latitude/longitude or near'
        args = {}

        if latitude and longitude:
            args['ll'] = ','.join([str(latitude), str(longitude)])
        if near:
            args['near'] = near
        if altitude:
            args['alt'] = altitude
        if latlng_accuracy:
            args['llAcc'] = latlng_accuracy
        if altitude_accuracy:
            args['altAcc'] = altitude_accuracy
        if query:
            args['query'] = query
        if limit:
            args['limit'] = int(limit)
        if url:
            args['url'] = url
        if categories:
            args['categoryId'] = ','.join(categories)
        if radius:
            args['radius'] = radius
        if sw:
            args['sw'] = sw
        if ne:
            args['ne'] = ne

        url = self._get_url('venues/search')
        return requests.get(url, params=args).json().get('response', {}).get('venues', [])

    # noinspection DuplicatedCode
    @action
    def explore(self,
                latitude: Optional[float] = None,
                longitude: Optional[float] = None,
                altitude: Optional[float] = None,
                latlng_accuracy: Optional[float] = None,
                altitude_accuracy: Optional[float] = None,
                section: Optional[str] = None,
                near: Optional[str] = None,
                query: Optional[str] = None,
                limit: Optional[int] = None,
                categories: Optional[List[str]] = None,
                radius: Optional[int] = None,
                open_now: bool = True,
                sort_by_distance: Optional[bool] = None,
                sort_by_popularity: Optional[bool] = None,
                price: Optional[List[int]] = None,
                saved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Explore venues around a location.

        :param latitude: Search near this latitude. Note either ``latitude, longitude`` or ``near`` should be provided.
        :param longitude: Search near this latitude. Note either ``latitude, longitude`` or ``near`` should be provided.
        :param near: Search near this place (e.g. "Chicago, IL" or "Amsterdam, NL"). Note either
            ``latitude, longitude`` or ``near`` should be provided.
        :param altitude: Search near this altitude in meters.
        :param latlng_accuracy:  Latitude/longitude accuracy in meters.
        :param altitude_accuracy: Altitude accuracy in meters.
        :param section: Section to search. Supported values:

            - food
            - drinks
            - coffee
            - shops
            - arts
            - outdoors
            - sights
            - trending
            - nextVenues

        :param query: Search query (e.g. "coffee shops" or "restaurants"). The parameter has no effect if
            ``section`` is specified.
        :param limit: Maximum number of results.
        :param categories: List of `category IDs <https://developer.foursquare.com/docs/resources/categories>`_
            to be searched.
        :param radius: Search radius in meters.
        :param open_now: Filter by open/not open now.
        :param sort_by_distance: Sort by distance.
        :param sort_by_popularity: Sort by popularity
        :param price: Price ranges, within the range ``[1,2,3,4]``.
        :param saved: Filter by saved/unsaved venues.

        :return: A list of venues, as returned by the Foursquare API.
        """
        assert (latitude and longitude) or near, 'Specify either latitude/longitude or near'
        args = {}

        if latitude and longitude:
            args['ll'] = ','.join([str(latitude), str(longitude)])
        if near:
            args['near'] = near
        if altitude:
            args['alt'] = altitude
        if latlng_accuracy:
            args['llAcc'] = latlng_accuracy
        if altitude_accuracy:
            args['altAcc'] = altitude_accuracy
        if section:
            args['section'] = section
        if query:
            args['query'] = query
        if categories:
            args['categoryId'] = ','.join(categories)
        if limit:
            args['limit'] = int(limit)
        if radius:
            args['radius'] = radius
        if open_now is not None:
            args['openNow'] = int(open_now)
        if sort_by_distance is not None:
            args['sortByDistance'] = int(sort_by_distance)
        if sort_by_popularity is not None:
            args['sortByPopularity'] = sort_by_popularity
        if saved is not None:
            args['saved'] = int(saved)
        if price:
            args['price'] = ','.join([str(p) for p in price])

        url = self._get_url('venues/explore')
        return requests.get(url, params=args).json().get('response', {}).get('venues', [])

    @action
    def trending(self,
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 near: Optional[str] = None,
                 limit: Optional[int] = None,
                 radius: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the trending venues around a location.

        :param latitude: Search near this latitude. Note either ``latitude, longitude`` or ``near`` should be provided.
        :param longitude: Search near this latitude. Note either ``latitude, longitude`` or ``near`` should be provided.
        :param near: Search near this place (e.g. "Chicago, IL" or "Amsterdam, NL"). Note either
            ``latitude, longitude`` or ``near`` should be provided.
        :param limit: Maximum number of results.
        :param radius: Search radius in meters.

        :return: A list of venues, as returned by the Foursquare API.
        """
        assert (latitude and longitude) or near, 'Specify either latitude/longitude or near'
        args = {}

        if latitude and longitude:
            args['ll'] = ','.join([str(latitude), str(longitude)])
        if near:
            args['near'] = near
        if limit:
            args['limit'] = int(limit)
        if radius:
            args['radius'] = radius

        url = self._get_url('venues/trending')
        return requests.get(url, params=args).json().get('response', {}).get('venues', [])

    @staticmethod
    def _parse_time(t):
        if isinstance(t, int) or isinstance(t, float):
            return datetime.datetime.fromtimestamp(t)
        if isinstance(t, str):
            return datetime.datetime.fromisoformat(t)

        assert isinstance(t, datetime.datetime), 'Cannot parse object of type {} into datetime: {}'.format(
            type(t), t)
        return t

    @action
    def time_series(self,
                    venue_id: Union[str, List[str]],
                    start_at: Union[int, float, datetime.datetime, str],
                    end_at: Union[int, float, datetime.datetime, str]) -> List[Dict[str, Any]]:
        """
        Get the visitors stats about one or multiple venues over a time range. The user must be a manager of
        those venues.

        :param venue_id: Venue ID or list of IDs to get the stats for.
        :param start_at: Stats start time. Can be a UNIX timestamp, a datetime object or an ISO format datetime.
        :param end_at: Stats end time. Can be a UNIX timestamp, a datetime object or an ISO format datetime.

        :return: A list of venues, as returned by the Foursquare API.
        """
        if isinstance(venue_id, list):
            venue_id = ','.join(venue_id)

        args = {
            'venueId': venue_id,
            'startAt': self._parse_time(start_at),
            'endAt': self._parse_time(end_at),
        }

        url = self._get_url('venues/timeseries')
        return requests.get(url, params=args).json().get('response', {}).get('venues', [])

    @action
    def stats(self,
              venue_id: str,
              start_at: Union[int, float, datetime.datetime, str],
              end_at: Union[int, float, datetime.datetime, str]) -> List[Dict[str, Any]]:
        """
        Get the stats about a venue over a time range. The user must be a manager of that venue.

        :param venue_id: Venue ID.
        :param start_at: Stats start time. Can be a UNIX timestamp, a datetime object or an ISO format datetime.
        :param end_at: Stats end time. Can be a UNIX timestamp, a datetime object or an ISO format datetime.

        :return: A list of venues, as returned by the Foursquare API.
        """
        args = {
            'startAt': self._parse_time(start_at),
            'endAt': self._parse_time(end_at),
        }

        url = self._get_url('venues/{}/stats'.format(venue_id))
        return requests.get(url, params=args).json().get('response', {}).get('venues', [])

    @action
    def managed(self) -> List[Dict[str, Any]]:
        """
        Get the list of venues managed by the user.
        :return: A list of venues, as returned by the Foursquare API.
        """
        url = self._get_url('venues/managed')
        return requests.get(url).json().get('response', {}).get('venues', []).get('items', [])

    @action
    def checkin(self,
                venue_id: str,
                latitude: Optional[float] = None,
                longitude: Optional[float] = None,
                altitude: Optional[float] = None,
                latlng_accuracy: Optional[float] = None,
                altitude_accuracy: Optional[float] = None,
                shout: Optional[str] = None,
                broadcast: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new check-in.

        :param venue_id: ID of the venue to check-in.
        :param latitude: Check-in latitude.
        :param longitude: Check-in longitude.
        :param altitude: Check-in altitude.
        :param latlng_accuracy:  Latitude/longitude accuracy in meters.
        :param altitude_accuracy: Altitude accuracy in meters.
        :param shout: Add a custom message to the check-in.
        :param broadcast: List of Visibility/share types of the check-in. Default: ``public``. Possible values are:

            - ``private``
            - ``public``
            - ``followers``
            - ``facebook``
            - ``twitter``

        :return: Foursquare API response.
        """
        args = {'venueId': venue_id}
        if latitude and longitude:
            args['ll'] = ','.join([str(latitude), str(longitude)])
        if altitude:
            args['alt'] = altitude
        if latlng_accuracy:
            args['llAcc'] = latlng_accuracy
        if altitude_accuracy:
            args['altAcc'] = altitude_accuracy
        if shout:
            args['shout'] = shout
        if broadcast:
            args['broadcast'] = ','.join(broadcast) if isinstance(broadcast, list) else broadcast

        url = self._get_url('checkins/add')
        return requests.post(url, data=args).json().get('response', {}).get('checkin', {})


# vim:sw=4:ts=4:et:
