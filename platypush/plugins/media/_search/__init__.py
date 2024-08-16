import logging
from abc import ABC, abstractmethod
from typing import Optional

from platypush.plugins import Plugin


class MediaSearcher(ABC):
    """
    Base class for media searchers
    """

    def __init__(self, *_, media_plugin: Optional[Plugin] = None, **__):
        from .. import MediaPlugin

        self.logger = logging.getLogger(self.__class__.__name__)
        assert isinstance(
            media_plugin, MediaPlugin
        ), f'Invalid media plugin: {media_plugin}'
        self.media_plugin: Optional[MediaPlugin] = media_plugin

    @abstractmethod
    def search(self, query, *args, **kwargs):
        raise NotImplementedError(
            'The search method should be implemented by a derived class'
        )

    @abstractmethod
    def supports(self, type: str) -> bool:
        raise NotImplementedError(
            'The type method should be implemented by a derived class'
        )


from .local import LocalMediaSearcher  # noqa: E402
from .youtube import YoutubeMediaSearcher  # noqa: E402
from .torrent import TorrentMediaSearcher  # noqa: E402
from .plex import PlexMediaSearcher  # noqa: E402
from .jellyfin import JellyfinMediaSearcher  # noqa: E402

searchers = [
    LocalMediaSearcher,
    YoutubeMediaSearcher,
    TorrentMediaSearcher,
    PlexMediaSearcher,
    JellyfinMediaSearcher,
]

__all__ = [
    'JellyfinMediaSearcher',
    'LocalMediaSearcher',
    'MediaSearcher',
    'PlexMediaSearcher',
    'TorrentMediaSearcher',
    'YoutubeMediaSearcher',
]


# vim:sw=4:ts=4:et:
