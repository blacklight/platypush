import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional


@dataclass
class YoutubeEntity(ABC):
    """
    Base class for YouTube objects.
    """

    url: str

    @property
    @abstractmethod
    def item_type(self) -> str:
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'url': self.url,
            'item_type': self.item_type,
            **{k: v for k, v in self.__dict__.items() if not k.startswith('_')},
        }


@dataclass
class YoutubeVideo(YoutubeEntity):
    """
    Dataclass for YouTube video items.
    """

    title: str
    channel: str
    channel_url: str
    duration: int = 0
    channel_image: Optional[str] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    image: Optional[str] = None
    index: Optional[int] = None
    index_id: Optional[str] = None
    next_page_token: Optional[Any] = None

    @property
    def item_type(self) -> str:
        return 'video'

    @property
    def id(self) -> str:
        return re.sub(r'^.*\/watch\?v=([^&]+).*$', r'\1', self.url)


@dataclass
class YoutubePlaylist(YoutubeEntity):
    """
    Dataclass for YouTube playlist items.
    """

    name: str
    channel: Optional[str] = None
    channel_url: Optional[str] = None
    videos: int = 0
    description: Optional[str] = None
    image: Optional[str] = None
    channel_image: Optional[str] = None
    next_page_token: Optional[Any] = None

    @property
    def item_type(self) -> str:
        return 'playlist'

    @property
    def id(self) -> str:
        return re.sub(r'^.*\/playlist\?list=([^&]+).*$', r'\1', self.url)


@dataclass
class YoutubeChannel(YoutubeEntity):
    """
    Dataclass for YouTube channel items.
    """

    name: str
    subscribers: int = 0
    next_page_token: Optional[Any] = None
    items: List[YoutubeEntity] = field(default_factory=list)
    image: Optional[str] = None
    description: Optional[str] = None
    banner: Optional[str] = None
    count: Optional[int] = None

    @property
    def item_type(self) -> str:
        return 'channel'

    @property
    def id(self) -> str:
        return re.sub(r'^.*\/channel/([^?]+).*$', r'\1', self.url)
