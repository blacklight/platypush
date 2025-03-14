import datetime
from typing import List, Dict, Any, Optional

import requests

from platypush.context import Variable
from platypush.message.event.foursquare import FoursquareCheckinEvent
from platypush.plugins import RunnablePlugin, action


class FoursquarePlugin(RunnablePlugin):
    """
    Plugin to interact with the `Foursquare Places API <https://developer.foursquare.com/docs/api>`_.

    It also raises events when a new check-in occurs on the user's account.

    In order to enable the Foursquare API on your account you need to:

        - Create a new app on the `Foursquare developers website <https://foursquare.com/developers/signup>`_.
        - Copy the ``client_id`` and ``client_secret``.
        - Add a redirect URL. It must point to a valid IP/hostname with a web server running, even if it runs
            locally. You can also use the local URL of the platypush web server - e.g. http://192.168.1.2:8008/.
        - Open the following URL:
            ``https://foursquare.com/oauth2/authenticate?client_id=CLIENT_ID&response_type=token&redirect_uri=REDIRECT_URI``.
            Replace ``CLIENT_ID`` and ``REDIRECT_URI`` with the parameters from your app.
        - Allow the application. You will be redirected to the URL you provided. Copy the ``access_token`` provided in
            the URL.

    """

    api_base_url = 'https://api.foursquare.com/v2'
    _last_created_at_varname = '_foursquare_checkin_last_created_at'
    _http_timeout = 10
    # API version to use, see https://docs.foursquare.com/developer/reference/versioning
    _api_version = '20240101'

    def __init__(self, access_token: str, poll_interval: float = 120, **kwargs):
        """
        :param poll_interval: Poll interval in seconds to check for new check-ins (default: 120).
            Set to 0 or ``None`` to disable polling of new check-ins.
        :param access_token: The access token to use to authenticate to the Foursquare API.
        """
        super().__init__(poll_interval=poll_interval, **kwargs)
        self.access_token = access_token
        self._last_created_at = Variable(self._last_created_at_varname)

    def _get_url(self, endpoint):
        return f'{self.api_base_url}/{endpoint}?oauth_token={self.access_token}&v={self._api_version}'

    def _get_checkins(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        url = self._get_url('users/self/checkins')
        return (
            requests.get(
                url,
                params={'limit': limit, 'offset': offset},
                timeout=self._http_timeout,
            )
            .json()
            .get('response', {})
            .get('checkins', {})
            .get('items', [])
        )

    @action
    def get_checkins(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get the list of check-ins of the current user.

        :param limit: Maximum number of check-ins to retrieve (default: 20).
        :param offset: Offset to start retrieving check-ins from (default: 0).
        :return: A list of checkins, as returned by the Foursquare API.
        """
        return self._get_checkins(limit=limit, offset=offset)

    @action
    def search(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        near: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        url: Optional[str] = None,
        categories: Optional[List[str]] = None,
        radius: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for venues.

        :param latitude: Search near this latitude. Note either ``latitude,
            longitude`` or ``near`` should be provided.
        :param longitude: Search near this latitude. Note either ``latitude,
            longitude`` or ``near`` should be provided.
        :param near: Search near this place (e.g. "Chicago, IL" or "Amsterdam,
            NL"). Note either ``latitude, longitude`` or ``near`` should be
            provided.
        :param query: Search query (e.g. "coffee shops" or "restaurants").
        :param limit: Maximum number of results.
        :param url: A 3rd-party URL associated to the venue to be searched.
        :param categories: List of `category IDs
            <https://developer.foursquare.com/docs/resources/categories>`_ to be
            searched.
        :param radius: Search radius in meters.
        :return: A list of venues, as returned by the Foursquare API.
        """
        assert (
            latitude and longitude
        ) or near, 'Specify either latitude/longitude or near'
        args = {}

        if latitude and longitude:
            args['ll'] = ','.join([str(latitude), str(longitude)])
        if near:
            args['near'] = near
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

        return (
            requests.get(
                self._get_url('venues/search'), params=args, timeout=self._http_timeout
            )
            .json()
            .get('response', {})
            .get('venues', [])
        )

    @action
    def explore(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        near: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        categories: Optional[List[str]] = None,
        radius: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Explore venues around a location.

        :param latitude: Search near this latitude. Note either ``latitude,
            longitude`` or ``near`` should be provided.
        :param longitude: Search near this latitude. Note either ``latitude,
            longitude`` or ``near`` should be provided.
        :param near: Search near this place (e.g. "Chicago, IL" or "Amsterdam,
            NL"). Note either ``latitude, longitude`` or ``near`` should be
            provided.
        :param query: Search query (e.g. "coffee shops" or "restaurants").
        :param limit: Maximum number of results.
        :param categories: List of `category IDs
            <https://developer.foursquare.com/docs/resources/categories>`_ to be
            searched.
        :param radius: Search radius in meters.

        :return: A list of venues, as returned by the Foursquare API.
        """
        assert (
            latitude and longitude
        ) or near, 'Specify either latitude/longitude or near'
        args = {}

        if latitude and longitude:
            args['ll'] = ','.join([str(latitude), str(longitude)])
        if near:
            args['near'] = near
        if query:
            args['query'] = query
        if categories:
            args['categoryId'] = ','.join(categories)
        if limit:
            args['limit'] = int(limit)
        if radius:
            args['radius'] = radius

        url = self._get_url('venues/search')
        return (
            requests.get(url, params=args, timeout=self._http_timeout)
            .json()
            .get('response', {})
            .get('venues', [])
        )

    @action
    def trending(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        near: Optional[str] = None,
        limit: Optional[int] = None,
        radius: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get the trending venues around a location.

        :param latitude: Search near this latitude. Note either ``latitude,
            longitude`` or ``near`` should be provided.
        :param longitude: Search near this latitude. Note either ``latitude,
            longitude`` or ``near`` should be provided.
        :param near: Search near this place (e.g. "Chicago, IL" or "Amsterdam,
            NL"). Note either ``latitude, longitude`` or ``near`` should be
            provided.
        :param limit: Maximum number of results.
        :param radius: Search radius in meters.

        :return: A list of venues, as returned by the Foursquare API.
        """
        assert (
            latitude and longitude
        ) or near, 'Specify either latitude/longitude or near'
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
        return (
            requests.get(url, params=args, timeout=self._http_timeout)
            .json()
            .get('response', {})
            .get('venues', [])
        )

    @staticmethod
    def _parse_time(t):
        if isinstance(t, (int, float)):
            return datetime.datetime.fromtimestamp(t)
        if isinstance(t, str):
            return datetime.datetime.fromisoformat(t)

        assert isinstance(
            t, datetime.datetime
        ), f'Cannot parse object of type {type(t)} into datetime: {t}'
        return t

    @action
    def checkin(
        self,
        venue_id: str,
        shout: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new check-in.

        :param venue_id: ID of the venue to check-in.
        :param shout: Add a custom message to the check-in.
        :return: Foursquare API response.
        """
        args = {'venueId': venue_id}
        if shout:
            args['shout'] = shout

        url = self._get_url('checkins/add')
        return (
            requests.post(url, data=args, timeout=self._http_timeout)
            .json()
            .get('response', {})
            .get('checkin', {})
        )

    def main(self):
        if not self.poll_interval:
            # If no poll interval is set then we won't poll for new check-ins
            self.wait_stop()
            return

        while not self.should_stop():
            try:
                checkins = self._get_checkins(limit=20, offset=0)
                if not checkins:
                    continue

                last_checkin = checkins[0]
                last_checkin_created_at = last_checkin.get('createdAt', 0)
                last_created_at = float(self._last_created_at.get() or 0)
                if last_created_at and last_checkin_created_at <= last_created_at:
                    continue

                self._bus.post(FoursquareCheckinEvent(checkin=last_checkin))
                self._last_created_at.set(last_checkin_created_at)
            finally:
                self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
