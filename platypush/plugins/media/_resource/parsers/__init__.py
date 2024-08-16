from ._base import MediaResourceParser
from .file import FileResourceParser
from .http import HttpResourceParser
from .torrent import TorrentResourceParser
from .youtube import YoutubeResourceParser


parsers = [
    FileResourceParser,
    YoutubeResourceParser,
    TorrentResourceParser,
    HttpResourceParser,
]


__all__ = [
    'MediaResourceParser',
    'FileResourceParser',
    'HttpResourceParser',
    'TorrentResourceParser',
    'YoutubeResourceParser',
    'parsers',
]


# vim:sw=4:ts=4:et:
