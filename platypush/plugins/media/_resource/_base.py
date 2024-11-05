import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from subprocess import Popen
from typing import IO, Iterable, Optional

from platypush.plugins import Plugin


@dataclass
class MediaResource(ABC):
    """
    Models a generic media resource.

    In this case resource/URL can be passed directly to the player.
    """

    resource: str
    url: str
    media_plugin: Plugin
    fd: Optional[IO] = None
    title: Optional[str] = None
    ext: Optional[str] = None
    description: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    image: Optional[str] = None
    duration: Optional[float] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    channel_url: Optional[str] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[str] = None
    timestamp: Optional[float] = None
    fps: Optional[float] = None
    audio_channels: Optional[int] = None
    view_count: Optional[int] = None
    categories: Optional[Iterable[str]] = field(default_factory=list)
    tags: Optional[Iterable[str]] = field(default_factory=list)

    @property
    def _logger(self):
        return logging.getLogger(self.__class__.__name__)

    @property
    def _media(self):
        """
        This workaround is required to avoid circular imports.
        """
        from platypush.plugins.media import MediaPlugin

        assert isinstance(self.media_plugin, MediaPlugin)
        return self.media_plugin

    @abstractmethod
    def open(self, *_, **__) -> IO:
        """
        Opens the media resource.
        """
        if self.fd is not None:
            try:
                self.fd.seek(0)
            except io.UnsupportedOperation:
                pass

        return self.fd

    def close(self) -> None:
        """
        Closes the media resource.
        """
        if self.fd is not None:
            self.fd.close()
            self.fd = None

    def __enter__(self) -> IO:
        """
        Opens the media resource using a context manager.
        """
        return self.open()

    def __exit__(self, *_, **__) -> None:
        """
        Closes the media resource using a context manager.
        """
        self.close()

    def to_dict(self) -> dict:
        """
        Converts the media resource to a dictionary ready to be serialized.
        """
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name not in ['media_plugin', 'fd']
        }


@dataclass
class PopenMediaResource(MediaResource, ABC):
    """
    Models a media resource that is read from a Popen object.
    """

    proc: Optional[Popen] = None

    def close(self) -> None:
        """
        Closes the media resource.
        """
        if self.proc is not None:
            self.proc.terminate()
            self.proc.wait(1)
            if self.proc and self.proc.poll() is None:
                self.proc.kill()
                self.proc.wait(1)

            self.proc = None

        super().close()

    def to_dict(self) -> dict:
        """
        Converts the media resource to a dictionary ready to be serialized.
        """
        ret = super().to_dict()
        ret.pop('proc', None)
        return ret


# vim:sw=4:ts=4:et:
