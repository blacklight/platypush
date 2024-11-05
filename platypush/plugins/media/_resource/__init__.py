from ._base import MediaResource
from .file import FileMediaResource
from .http import HttpMediaResource
from .youtube import YoutubeMediaResource


__all__ = [
    'FileMediaResource',
    'HttpMediaResource',
    'MediaResource',
    'YoutubeMediaResource',
]
