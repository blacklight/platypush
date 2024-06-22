from typing import List

import requests

from .._model import TorrentSearchResult
from ._base import TorrentsCsvBaseProvider


class TorrentsCsvAPIProvider(TorrentsCsvBaseProvider):
    """
    Torrent that uses `Torrents.csv <https://torrents-csv.com/>`_ or any other
    `Torrents.csv API <https://torrents-csv.com/service>`_ instance to search
    for torrents.
    """

    def __init__(self, api_url: str, **kwargs):
        """
        :param api_url: Torrents.csv API base URL.
        """
        super().__init__(**kwargs)
        self.api_url = api_url

    def _search(
        self, query: str, *_, limit: int, page: int, **__
    ) -> List[TorrentSearchResult]:
        """
        Perform a search of torrents using the Torrent.csv API.

        :param query: Query string.
        :param limit: Number of results to return (default: 25).
        :param page: Page number (default: 1).
        """
        response = requests.get(
            f'{self.api_url}/search',
            params={
                'q': query,
                'size': limit,
                'page': page,
            },
            timeout=self._http_timeout,
        )

        response.raise_for_status()
        return [
            TorrentSearchResult(
                title=torrent.get('name', '[No Title]'),
                url=self._to_magnet(
                    info_hash=torrent.get('infohash'), torrent_name=torrent.get('name')
                ),
                size=torrent.get('size_bytes'),
                created_at=torrent.get('created_unix'),
                seeds=torrent.get('seeders'),
                peers=torrent.get('leechers'),
            )
            for torrent in response.json().get('torrents', [])
        ]


# vim:sw=4:ts=4:et:
