from platypush.context import get_plugin
from platypush.plugins.media._search import MediaSearcher


# pylint: disable=too-few-public-methods
class TorrentMediaSearcher(MediaSearcher):
    """
    Media searcher for torrents.

    It needs at least one torrent plugin to be configured.
    """

    def search(self, query: str, *_, limit=None, page_state=None, **__):
        self.logger.info('Searching torrents for "%s"', query)

        torrents = get_plugin(
            self.media_plugin.torrent_plugin if self.media_plugin else 'torrent'
        )

        if not torrents:
            raise RuntimeError('Torrent plugin not available/configured')

        limit = limit or self._default_limit
        page = (page_state or {}).get('page', 1)

        raw_results = torrents.search(query, limit=limit, page=page).output
        results = [t for t in raw_results if t.get('is_media')]

        next_state = {'page': page + 1} if len(raw_results) >= limit else None
        return results, next_state

    def supports(self, type: str) -> bool:
        return type == 'torrent'


# vim:sw=4:ts=4:et:
