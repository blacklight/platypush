import logging


class MediaSearcher:
    """
    Base class for media searchers
    """

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

    def search(self, query, *args, **kwargs):
        raise NotImplementedError('The search method should be implemented ' +
                                  'by a derived class')


from .local import LocalMediaSearcher
from .youtube import YoutubeMediaSearcher
from .torrent import TorrentMediaSearcher

__all__ = ['LocalMediaSearcher', 'TorrentMediaSearcher', 'YoutubeMediaSearcher']


# vim:sw=4:ts=4:et:
