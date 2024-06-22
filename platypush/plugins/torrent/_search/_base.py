from abc import ABC, abstractmethod
from logging import getLogger
from typing import Iterable

from ._model import TorrentSearchResult


class TorrentSearchProvider(ABC):
    """
    Base class for torrent search providers.
    """

    def __init__(self, **kwargs):
        if 'enabled' in kwargs:
            self.enabled = bool(kwargs['enabled'])
        elif 'disabled' in kwargs:
            self.enabled = not bool(kwargs['disabled'])
        else:
            self.enabled = self.default_enabled()

        self.logger = getLogger(self.__class__.__name__)

    @abstractmethod
    def _search(self, query: str, *args, **kwargs) -> Iterable[TorrentSearchResult]:
        """
        Inner search method. This method should be implemented by subclasses.

        :param query: Query string, torrent name or partial name.
        """
        return []

    @classmethod
    @abstractmethod
    def provider_name(cls) -> str:
        """
        :return: Name of the provider, which can be used to identify it within
            the :class:`platypush.plugins.torrent.TorrentPlugin`.
        """

    def search(self, query: str, *args, **kwargs) -> Iterable[TorrentSearchResult]:
        """
        Perform a search of torrents.

        :param query: Query string, torrent name or partial name.
        """
        if not self.enabled:
            self.logger.debug(
                'Provider %s is disabled, skipping search', self.__class__.__name__
            )
            return []

        self.logger.debug("Searching for %r", query)
        return self._search(query, *args, **kwargs)

    @classmethod
    def default_enabled(cls) -> bool:
        """
        :return: True if the provider is enabled by default, False otherwise.
          Default: False.
        """
        return False


# vim:sw=4:ts=4:et:
