from abc import ABC, abstractmethod
from logging import getLogger
from typing import Optional

from .. import MediaResource


# pylint: disable=too-few-public-methods
class MediaResourceParser(ABC):
    """
    Base class for media resource parsers.
    """

    def __init__(self, media_plugin, *_, **__):
        from platypush.plugins.media import MediaPlugin

        self._media: MediaPlugin = media_plugin
        self.logger = getLogger(self.__class__.__name__)

    @abstractmethod
    def parse(self, resource: str, *_, **__) -> Optional[MediaResource]:
        """
        Parses a media resource and returns a MediaResource object.
        """
        raise NotImplementedError


# vim:sw=4:ts=4:et:
