from platypush.context import get_plugin
from platypush.plugins.media.search import MediaSearcher


# pylint: disable=too-few-public-methods
class YoutubeMediaSearcher(MediaSearcher):
    """
    Search YouTube videos by query.
    """

    def search(self, query: str, *_, **__):
        """
        Performs a YouTube search using the ``youtube`` plugin.
        """

        self.logger.info('Searching YouTube for "%s"', query)
        yt = get_plugin('youtube')
        assert yt, 'YouTube plugin not available/configured'
        return yt.search(query=query).output


# vim:sw=4:ts=4:et:
