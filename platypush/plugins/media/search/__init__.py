import logging
from typing import Optional

from .. import MediaPlugin


class MediaSearcher:
    """
    Base class for media searchers
    """

    def __init__(self, *args, media_plugin: Optional[MediaPlugin] = None, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.media_plugin = media_plugin

    def search(self, query, *args, **kwargs):
        raise NotImplementedError('The search method should be implemented ' +
                                  'by a derived class')


from .local import LocalMediaSearcher
from .youtube import YoutubeMediaSearcher
from .torrent import TorrentMediaSearcher
from .plex import PlexMediaSearcher
from .jellyfin import JellyfinMediaSearcher

__all__ = [
    'MediaSearcher', 'LocalMediaSearcher', 'TorrentMediaSearcher',
    'YoutubeMediaSearcher', 'PlexMediaSearcher', 'JellyfinMediaSearcher',
]


# vim:sw=4:ts=4:et:
