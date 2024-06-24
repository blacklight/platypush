from platypush.context import get_plugin
from platypush.plugins.media.search import MediaSearcher


class TorrentMediaSearcher(MediaSearcher):
    def search(self, query, **kwargs):
        self.logger.info('Searching torrents for "{}"'.format(query))

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


# vim:sw=4:ts=4:et:
