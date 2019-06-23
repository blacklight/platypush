from platypush.context import get_plugin
from platypush.plugins.media.search import MediaSearcher

class TorrentMediaSearcher(MediaSearcher):
    def search(self, query):
        self.logger.info('Searching torrents for "{}"'.format(query))

        torrents = get_plugin('torrent')
        if not torrents:
            raise RuntimeError('Torrent plugin not available/configured')
        return torrents.search(query, ).output



# vim:sw=4:ts=4:et:
