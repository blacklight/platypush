import urllib.parse

import requests

from platypush.plugins import Plugin, action


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

    def __init__(self, piped_api_url: str = 'https://pipedapi.kavin.rocks', **kwargs):
        """
        :param piped_api_url: Base API URL of the Piped instance (default:
            ``https://pipedapi.kavin.rocks``).
        """
        super().__init__(**kwargs)
        self._piped_api_url = piped_api_url

    @action
    def search(self, query: str, **_):
        """
        Search for YouTube videos.

        :param query: Query string.

        :return: A list of results in the following format:

            .. code-block:: json

                {
                    "url": "https://www.youtube.com/watch?v=..."
                    "title": "Video title",
                    "description": "Video description",
                    "image": "https://i.ytimg.com/vi/.../hqdefault.jpg",
                    "duration": 300
                }

        """
        self.logger.info('Searching YouTube for "%s"', query)
        query = urllib.parse.quote(query)
        url = f"{self._piped_api_url}/search?q=" + query + "&filter=all"
        rs = requests.get(url, timeout=20)
        rs.raise_for_status()
        results = [
            {
                "url": "https://www.youtube.com" + item["url"],
                "title": item["title"],
                "image": item["thumbnail"],
                "duration": item["duration"],
                "description": item["shortDescription"],
            }
            for item in rs.json().get("items", [])
        ]

        self.logger.info(
            '%d YouTube video results for the search query "%s"',
            len(results),
            query,
        )

        return results


# vim:sw=4:ts=4:et:
