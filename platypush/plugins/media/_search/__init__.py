import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from platypush.plugins import Plugin


class MediaSearcher(ABC):
    """
    Base class for media searchers
    """

    _default_limit = 25

    def __init__(self, *_, media_plugin: Optional[Plugin] = None, **__):
        from .. import MediaPlugin

        self.logger = logging.getLogger(self.__class__.__name__)
        if not isinstance(media_plugin, MediaPlugin):
            raise AssertionError(f'Invalid media plugin: {media_plugin}')
        self.media_plugin: Optional[MediaPlugin] = media_plugin

    @abstractmethod
    def search(
        self,
        query: str,
        *args,
        limit: Optional[int] = None,
        page_state: Optional[Dict] = None,
        **kwargs,
    ) -> Tuple[List[dict], Optional[Dict]]:
        """
        Search for media items.

        :param query: Search query string.
        :param limit: Maximum number of results to return per page.
        :param page_state: Opaque per-searcher pagination state from a
            previous search response.
        :return: A tuple of ``(results, next_page_state)``.  When
            ``next_page_state`` is ``None`` there are no more pages.
        """
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
    'searchers',
]


# vim:sw=4:ts=4:et:
