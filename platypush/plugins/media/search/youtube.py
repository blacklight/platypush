import re
import urllib.parse
import urllib.request

import requests

from platypush.context import get_plugin
from platypush.plugins.media.search import MediaSearcher


# pylint: disable=too-few-public-methods
class YoutubeMediaSearcher(MediaSearcher):
    """
    Search YouTube videos by query.
    """

    def search(self, query: str, *_, **__):
        """
        Performs a YouTube search either using the YouTube API (faster and
        recommended, it requires the :mod:`platypush.plugins.google.youtube`
        plugin to be configured) or parsing the HTML search results (fallback
        slower method)
        """

        self.logger.info('Searching YouTube for "%s"', query)

        try:
            return self._youtube_search_api(query=query)
        except Exception as e:
            self.logger.warning(
                (
                    'Unable to load the YouTube plugin, '
                    'falling back to HTML parse method: %s'
                ),
                e,
            )

        return self._youtube_search_html_parse(query=query)

    @staticmethod
    def _youtube_search_api(query):
        yt = get_plugin('google.youtube')
        assert yt, 'YouTube plugin not configured'
        return [
            {
                'url': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                **item.get('snippet', {}),
            }
            for item in yt.search(query=query).output
            if item.get('id', {}).get('kind') == 'youtube#video'
        ]

    def _youtube_search_html_parse(self, query):
        query = urllib.parse.quote(query)
        url = "https://www.youtube.com/results?search_query=" + query
        html = requests.get(url, timeout=10).content
        results = []

        while html:
            m = re.search(
                r'(<a href="(/watch\?v=.+?)".+?yt-uix-tile-link.+?title="(.+?)".+?>)',
                html,
            )
            if m:
                results.append(
                    {'url': 'https://www.youtube.com' + m.group(2), 'title': m.group(3)}
                )

                html = html.split(m.group(1))[1]
            else:
                html = ''

        self.logger.info(
            '%d YouTube video results for the search query "%s"',
            len(results),
            query,
        )

        return results


# vim:sw=4:ts=4:et:
