from platypush.context import get_plugin
from platypush.plugins.media._search import MediaSearcher


# pylint: disable=too-few-public-methods
class TorrentMediaSearcher(MediaSearcher):
    """
    Media searcher for torrents.

    It needs at least one torrent plugin to be configured.
    """

    def search(self, query: str, *_, **__):
        self.logger.info('Searching torrents for "%s"', query)

        torrents = get_plugin(
            self.media_plugin.torrent_plugin if self.media_plugin else 'torrent'
        )

        if not torrents:
            raise RuntimeError('Torrent plugin not available/configured')

        return [
            torrent
            for torrent in torrents.search(
                query,
            ).output
            if torrent.get('is_media')
        ]

    def supports(self, type: str) -> bool:
        return type == 'torrent'


# vim:sw=4:ts=4:et:
