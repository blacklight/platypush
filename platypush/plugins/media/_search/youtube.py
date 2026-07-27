from platypush.context import get_plugin
from platypush.plugins.media._search import MediaSearcher


# pylint: disable=too-few-public-methods
class YoutubeMediaSearcher(MediaSearcher):
    """
    Search YouTube videos by query.
    """

    def search(self, query: str, *_, page_state=None, **__):
        """
        Performs a YouTube search using the ``youtube`` plugin.
        """

        self.logger.info('Searching YouTube for "%s"', query)
        yt = get_plugin('youtube')
        if not (yt):
            raise AssertionError('YouTube plugin not available/configured')

        page = (page_state or {}).get('page')
        results = yt.search(query=query, page=page).output

        next_page = None
        if results:
            next_page = results[-1].get('next_page_token')

        next_state = {'page': next_page} if next_page is not None else None
        return results, next_state

    def supports(self, type: str) -> bool:
        return type == 'youtube'


# vim:sw=4:ts=4:et:
