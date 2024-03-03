from abc import ABC, abstractmethod
import hashlib
import logging
import os
from typing import Generator, Optional

from platypush.message import JSONAble


class MediaHandler(JSONAble, ABC):
    """
    Abstract class to manage media handlers that can be streamed over the HTTP
    server through the `/media` endpoint.
    """

    prefix_handlers = []

    def __init__(
        self,
        source: str,
        *_,
        filename: Optional[str] = None,
        mime_type: str = 'application/octet-stream',
        name: Optional[str] = None,
        url: Optional[str] = None,
        subtitles: Optional[str] = None,
        **__,
    ):
        matched_handlers = [
            hndl for hndl in self.prefix_handlers if source.startswith(hndl)
        ]

        if not matched_handlers:
            raise AttributeError(
                f'No matched handlers found for source "{source}" '
                f'through {self.__class__.__name__}. Supported handlers: {self.prefix_handlers}'
            )

        self.name = name
        self.path = None
        self.filename = filename
        self.source = source
        self.url = url
        self.mime_type = mime_type
        self.subtitles = subtitles
        self.content_length = 0
        self._matched_handler = matched_handlers[0]

    @classmethod
    def build(cls, source: str, *args, **kwargs) -> 'MediaHandler':
        errors = {}

        for hndl_class in supported_handlers:
            try:
                return hndl_class(source, *args, **kwargs)
            except Exception as e:
                logging.exception(e)
                errors[hndl_class.__name__] = str(e)

        if os.path.exists(source):
            source = f'file://{source}'

        raise AttributeError(
            f'The source {source} has no handlers associated. Errors: {errors}'
        )

    @abstractmethod
    def get_data(
        self,
        from_bytes: Optional[int] = None,
        to_bytes: Optional[int] = None,
        chunk_size: Optional[int] = None,
    ) -> Generator[bytes, None, None]:
        raise NotImplementedError()

    @property
    def media_id(self) -> str:
        """
        :returns: The unique ID of the media handler.
        """
        return self.get_media_id(self.source)

    def set_subtitles(self, subtitles_file: Optional[str]):
        self.subtitles = subtitles_file

    def remove_subtitles(self):
        self.subtitles = None

    def __iter__(self):
        """
        Iterate over the attributes of the media handler.
        """
        for attr in [
            'name',
            'source',
            'mime_type',
            'url',
            'subtitles',
            'prefix_handlers',
            'media_id',
        ]:
            if hasattr(self, attr):
                yield attr, getattr(self, attr)

    @staticmethod
    def get_media_id(source: str) -> str:
        """
        :returns: The ID of a media file given its source.
        """
        return hashlib.sha1(source.encode()).hexdigest()

    def to_json(self):
        """
        :returns: A dictionary representation of the media handler.
        """
        return dict(self)


from .file import FileHandler  # noqa

__all__ = ['MediaHandler', 'FileHandler']


supported_handlers = [eval(hndl) for hndl in __all__ if hndl != MediaHandler.__name__]


# vim:sw=4:ts=4:et:
