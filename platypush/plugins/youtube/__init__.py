from typing import Optional

import requests

from platypush.plugins import Plugin, action
from platypush.schemas.piped import PipedVideoSchema


class YoutubePlugin(Plugin):
    r"""
    YouTube plugin.

    Unlike other Google plugins, this plugin doesn't rely on the Google API.

    That's because the official YouTube API has been subject to many changes to
    prevent scraping, and it requires the user to tinker with the OAuth layer,
    app permissions and app validation in order to get it working.

    Instead, it relies on a `Piped <https://docs.piped.video/`_, an open-source
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

    def _request(self, path: str, auth: bool = True, **kwargs):
        timeout = kwargs.pop('timeout', self._timeout)
        if auth:
            kwargs['params'] = kwargs.get('params', {})
            kwargs['params']['authToken'] = self._auth_token

        rs = requests.get(self._api_url(path), timeout=timeout, **kwargs)
        rs.raise_for_status()
        return rs.json()

    @action
    def search(self, query: str, **_):
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
    def get_feed(self):
        """
        Retrieve the YouTube feed.

        Depending on your account settings on the configured Piped instance,
        this may return either the latest videos uploaded by your subscribed
        channels, or the trending videos in the configured area.

        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        return PipedVideoSchema(many=True).dump(self._request('feed')) or []


# vim:sw=4:ts=4:et:
