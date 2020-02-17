import re
import urllib.parse
import urllib.request

from platypush.context import get_plugin
# noinspection PyProtectedMember
from platypush.plugins.media.search import MediaSearcher


class YoutubeMediaSearcher(MediaSearcher):
    def search(self, query, **kwargs):
        """
        Performs a YouTube search either using the YouTube API (faster and
        recommended, it requires the :mod:`platypush.plugins.google.youtube`
        plugin to be configured) or parsing the HTML search results (fallback
        slower method)
        """

        self.logger.info('Searching YouTube for "{}"'.format(query))

        try:
            return self._youtube_search_api(query=query)
        except Exception as e:
            self.logger.warning('Unable to load the YouTube plugin, falling ' +
                                'back to HTML parse method: {}'.format(str(e)))

            return self._youtube_search_html_parse(query=query)

    @staticmethod
    def _youtube_search_api(query):
        return [
            {
                'url': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                **item.get('snippet', {}),
            }
            for item in get_plugin('google.youtube').search(query=query).output
            if item.get('id', {}).get('kind') == 'youtube#video'
        ]

    def _youtube_search_html_parse(self, query):
        query = urllib.parse.quote(query)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
        results = []

        while html:
            m = re.search('(<a href="(/watch\?v=.+?)".+?yt-uix-tile-link.+?title="(.+?)".+?>)', html)
            if m:
                results.append({
                    'url': 'https://www.youtube.com' + m.group(2),
                    'title': m.group(3)
                })

                html = html.split(m.group(1))[1]
            else:
                html = ''

        self.logger.info('{} YouTube video results for the search query "{}"'
                         .format(len(results), query))

        return results


# vim:sw=4:ts=4:et:
