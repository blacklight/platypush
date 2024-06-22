from abc import ABC, abstractmethod
from logging import getLogger
from typing import List, Optional
from urllib.parse import quote_plus

from .._base import TorrentSearchProvider
from .._model import TorrentSearchResult


class TorrentsCsvBaseProvider(TorrentSearchProvider, ABC):
    """
    Base class for Torrents.csv search providers.
    """

    _http_timeout = 20
    _magnet_trackers = [
        'http://125.227.35.196:6969/announce',
        'http://210.244.71.25:6969/announce',
        'http://210.244.71.26:6969/announce',
        'http://213.159.215.198:6970/announce',
        'http://37.19.5.139:6969/announce',
        'http://37.19.5.155:6881/announce',
        'http://87.248.186.252:8080/announce',
        'http://asmlocator.ru:34000/1hfZS1k4jh/announce',
        'http://bt.evrl.to/announce',
        'http://bt.rutracker.org/ann',
        'https://www.artikelplanet.nl',
        'http://mgtracker.org:6969/announce',
        'http://tracker.baravik.org:6970/announce',
        'http://tracker.dler.org:6969/announce',
        'http://tracker.filetracker.pl:8089/announce',
        'http://tracker.grepler.com:6969/announce',
        'http://tracker.mg64.net:6881/announce',
        'http://tracker.tiny-vps.com:6969/announce',
        'http://tracker.torrentyorg.pl/announce',
        'https://internet.sitelio.me/',
        'https://computer1.sitelio.me/',
        'udp://168.235.67.63:6969',
        'udp://37.19.5.155:2710',
        'udp://46.148.18.250:2710',
        'udp://46.4.109.148:6969',
        'udp://computerbedrijven.bestelinks.nl/',
        'udp://computerbedrijven.startsuper.nl/',
        'udp://computershop.goedbegin.nl/',
        'udp://c3t.org',
        'udp://allerhandelenlaag.nl',
        'udp://tracker.opentrackr.org:1337',
        'udp://tracker.publicbt.com:80',
        'udp://tracker.tiny-vps.com:6969',
        'udp://tracker.openbittorrent.com:80',
        'udp://opentor.org:2710',
        'udp://tracker.ccc.de:80',
        'udp://tracker.blackunicorn.xyz:6969',
        'udp://tracker.coppersurfer.tk:6969',
        'udp://tracker.leechers-paradise.org:6969',
    ]

    def __init__(
        self,
        trackers: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        :param trackers: List of additional trackers to use.
        """
        super().__init__(**kwargs)
        self.logger = getLogger(self.__class__.__name__)
        self.trackers = list({*self._magnet_trackers, *(trackers or [])})

    @classmethod
    def provider_name(cls) -> str:
        return 'torrents.csv'

    @abstractmethod
    def _search(  # pylint: disable=arguments-differ
        self, query: str, *_, limit: int, page: int, **__
    ) -> List[TorrentSearchResult]:
        """
        To be implemented by subclasses.

        :param query: Query string.
        :param limit: Number of results to return (default: 25).
        :param page: Page number (default: 1).
        """

    def _to_magnet(self, info_hash: str, torrent_name: str) -> str:
        """
        Generate a magnet link from an info hash and torrent name.

        :param info_hash: Torrent info hash.
        :param torrent_name: Torrent name.
        :return: Magnet link.
        """
        return (
            f'magnet:?xt=urn:btih:{info_hash}&dn={quote_plus(torrent_name)}&tr='
            + '&tr='.join([quote_plus(tracker) for tracker in self.trackers])
        )


# vim:sw=4:ts=4:et:
