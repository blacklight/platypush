import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Collection, List, Optional

from ..model import YoutubeChannel, YoutubeEntity, YoutubePlaylist, YoutubeVideo


@dataclass
class BaseBackend(ABC):
    """
    Base class for YouTube backends.
    """

    instance_url: str
    auth_token: Optional[str] = None
    timeout: float = 20

    @property
    def name(self) -> str:
        return '_'.join(
            re.sub(r'([a-z])([A-Z])', r'\1_\2', self.__class__.__name__).split('_')[:-1]
        ).lower()

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    @abstractmethod
    def _request(
        self, path: str, method: str = 'get', body: Optional[str] = None, **kwargs
    ) -> Any:
        pass

    @abstractmethod
    def search(
        self, query: str, page: Optional[Any] = 1, sort=None, **kwargs
    ) -> List[YoutubeEntity]:
        pass

    @abstractmethod
    def get_feed(self, **_) -> List[YoutubeVideo]:
        pass

    @abstractmethod
    def get_playlists(self, **_) -> List[YoutubePlaylist]:
        pass

    @abstractmethod
    def get_playlist(self, id: str, **_) -> List[YoutubeVideo]:
        pass

    @abstractmethod
    def get_subscriptions(self, **_) -> List[YoutubeChannel]:
        pass

    @abstractmethod
    def get_channel(self, id: str, **_) -> YoutubeChannel:
        pass

    @abstractmethod
    def add_to_playlist(
        self, playlist_id: str, item_ids: Optional[Collection[str]] = None, **kwargs
    ):
        pass

    @abstractmethod
    def remove_from_playlist(
        self,
        playlist_id: str,
        item_ids: Optional[Collection[str]] = None,
        indices: Optional[Collection[int]] = None,
        **kwargs,
    ):
        pass

    @abstractmethod
    def create_playlist(self, name: str, **_) -> YoutubePlaylist:
        pass

    @abstractmethod
    def edit_playlist(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **_,
    ):  # pylint: disable=redefined-builtin
        pass

    @abstractmethod
    def delete_playlist(self, id: str):  # pylint: disable=redefined-builtin
        pass

    @abstractmethod
    def is_subscribed(self, channel_id: str) -> bool:
        pass

    @abstractmethod
    def subscribe(self, channel_id: str):
        pass

    @abstractmethod
    def unsubscribe(self, channel_id: str):
        pass

    @staticmethod
    def _get_video_id(id_or_url: str) -> str:
        m = re.search(r'/watch\?v=([^&]+)', id_or_url)
        if m:
            return m.group(1)

        return id_or_url


# vim:sw=4:ts=4:et:
