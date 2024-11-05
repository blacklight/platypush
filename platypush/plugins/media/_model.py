import enum
from dataclasses import dataclass, field
from typing import Optional


class PlayerState(enum.Enum):
    """
    Models the possible states of a media player
    """

    STOP = 'stop'
    PLAY = 'play'
    PAUSE = 'pause'
    IDLE = 'idle'


class DownloadState(enum.Enum):
    """
    Enum that represents the status of a download.
    """

    IDLE = 'idle'
    STARTED = 'started'
    DOWNLOADING = 'downloading'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ERROR = 'error'


@dataclass
class MediaDirectoryIcon:
    """
    Dataclass that represents a media directory icon.
    """

    class_: str = 'fas fa-folder'
    url: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Convert the MediaDirectoryIcon instance to a dictionary.
        """
        return {'class': self.class_, 'url': self.url}


@dataclass
class MediaDirectory:
    """
    Dataclass that represents a media directory.
    """

    name: str
    path: str
    icon: MediaDirectoryIcon = field(default_factory=MediaDirectoryIcon)

    @classmethod
    def build(
        cls,
        name: str,
        path: str,
        icon_class: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> 'MediaDirectory':
        """
        Create a MediaDirectory instance from a dictionary.
        """
        icon_class = icon_class or 'fas fa-folder'
        return cls(name, path, MediaDirectoryIcon(icon_class, icon_url))

    def to_dict(self) -> dict:
        """
        Convert the MediaDirectory instance to a dictionary.
        """
        return {'name': self.name, 'path': self.path, 'icon': self.icon.to_dict()}


# vim:sw=4:ts=4:et:
