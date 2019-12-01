from platypush.plugins import action
from platypush.plugins.http.request import HttpRequestPlugin

class HttpRequestRssPlugin(HttpRequestPlugin):
    """
    Plugin to programmatically retrieve and parse an RSS feed URL.

    Requires:

        * **feedparser** (``pip install feedparser``)
    """

    @action
    def get(self, url):
        import feedparser
        response = super().get(url, output='text').output
        feed = feedparser.parse(response)
        return feed.entries


# vim:sw=4:ts=4:et:

