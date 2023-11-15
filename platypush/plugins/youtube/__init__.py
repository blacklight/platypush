import base64
from functools import lru_cache
from typing import List, Optional

import requests

from platypush.plugins import Plugin, action
from platypush.schemas.piped import (
    PipedChannelSchema,
    PipedPlaylistSchema,
    PipedVideoSchema,
)


class YoutubePlugin(Plugin):
    r"""
    YouTube plugin.

    Unlike other Google plugins, this plugin doesn't rely on the Google API.

    That's because the official YouTube API has been subject to many changes to
    prevent scraping, and it requires the user to tinker with the OAuth layer,
    app permissions and app validation in order to get it working.

    Instead, it relies on a `Piped <https://docs.piped.video/>`_, an open-source
    alternative YouTube gateway.

    It thus requires a link to a valid Piped instance.
    """

    _timeout = 20

    def __init__(
        self,
        piped_api_url: str = 'https://pipedapi.kavin.rocks',
        auth_token: Optional[str] = None,
        **kwargs,
    ):
        """
        :param piped_api_url: Base API URL of the Piped instance (default:
            ``https://pipedapi.kavin.rocks``).
        :param auth_token: Optional authentication token from the Piped
            instance. This is required if you want to access your private feed
            and playlists, but not for searching public videos.

            In order to retrieve an authentication token:

              1. Login to your configured Piped instance.
              2. Copy the RSS/Atom feed URL on the _Feed_ tab.
              3. Copy the ``auth_token`` query parameter from the URL.
              4. Enter it in the ``auth_token`` field in the ``youtube`` section
                 of the configuration file.

        """
        super().__init__(**kwargs)
        self._piped_api_url = piped_api_url
        self._auth_token = auth_token

    def _api_url(self, path: str = '') -> str:
        return f"{self._piped_api_url}/{path}"

    def _request(
        self, path: str, body: Optional[str] = None, auth: bool = True, **kwargs
    ):
        timeout = kwargs.pop('timeout', self._timeout)
        if auth:
            kwargs['params'] = kwargs.get('params', {})
            kwargs['params']['authToken'] = self._auth_token
            kwargs['headers'] = kwargs.get('headers', {})
            kwargs['headers']['Authorization'] = self._auth_token

        if body:
            kwargs['data'] = body

        rs = requests.get(self._api_url(path), timeout=timeout, **kwargs)
        rs.raise_for_status()
        return rs.json()

    @lru_cache(maxsize=10)  # noqa
    def _get_channel(self, id: str) -> dict:  # pylint: disable=redefined-builtin
        if (
            id.startswith('http')
            or id.startswith('https')
            or id.startswith('/channel/')
        ):
            id = id.split('/')[-1]

        return (
            PipedChannelSchema().dump(self._request(f'channel/{id}')) or {}  # type: ignore
        )

    @action
    def search(self, query: str, **_) -> List[dict]:
        """
        Search for YouTube videos.

        :param query: Query string.
        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        self.logger.info('Searching YouTube for "%s"', query)
        rs = self._request('search', auth=False, params={'q': query, 'filter': 'all'})
        results = PipedVideoSchema(many=True).dump(rs.get("items", [])) or []
        self.logger.info(
            '%d YouTube video results for the search query "%s"',
            len(results),
            query,
        )

        return results

    @action
    def get_feed(self) -> List[dict]:
        """
        Retrieve the YouTube feed.

        Depending on your account settings on the configured Piped instance,
        this may return either the latest videos uploaded by your subscribed
        channels, or the trending videos in the configured area.

        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        return PipedVideoSchema(many=True).dump(self._request('feed')) or []

    @action
    def get_playlists(self) -> List[dict]:
        """
        Retrieve the playlists saved by the user logged in to the Piped
        instance.

        :return: .. schema:: piped.PipedPlaylistSchema(many=True)
        """
        return (
            PipedPlaylistSchema(many=True).dump(self._request('user/playlists')) or []
        )

    @action
    def get_playlist(self, id: str) -> List[dict]:  # pylint: disable=redefined-builtin
        """
        Retrieve the videos in a playlist.

        :param id: Piped playlist ID.
        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        return (
            PipedVideoSchema(many=True).dump(
                self._request(f'playlists/{id}').get('relatedStreams', [])
            )
            or []
        )

    @action
    def get_subscriptions(self) -> List[dict]:
        """
        Retrieve the channels subscribed by the user logged in to the Piped
        instance.

        :return: .. schema:: piped.PipedChannelSchema(many=True)
        """
        return PipedChannelSchema(many=True).dump(self._request('subscriptions')) or []

    @action
    def get_channel(
        self,
        id: str,  # pylint: disable=redefined-builtin
        next_page_token: Optional[str] = None,
    ) -> dict:
        """
        Retrieve the information and videos of a channel given its ID or URL.

        :param id: Channel ID or URL.
        :param next_page_token: Optional token to retrieve the next page of
            results.
        :return: .. schema:: piped.PipedChannelSchema
        """
        if (
            id.startswith('http')
            or id.startswith('https')
            or id.startswith('/channel/')
        ):
            id = id.split('/')[-1]

        info = {}
        if next_page_token:
            info = self._get_channel(id).copy()
            info.pop('next_page_token', None)
            info['items'] = []
            next_page = base64.b64decode(next_page_token.encode()).decode()
            response = {
                **info,
                **self._request(
                    f'nextpage/channel/{id}', params={'nextpage': next_page}, auth=False
                ),
            }
        else:
            response = self._request(f'channel/{id}')

        return PipedChannelSchema().dump(response) or {}  # type: ignore


# vim:sw=4:ts=4:et:
