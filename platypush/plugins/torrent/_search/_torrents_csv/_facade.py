import os
from typing import List, Optional

from .._model import TorrentSearchResult
from ._base import TorrentsCsvBaseProvider
from ._constants import (
    TORRENT_CSV_API_URL,
    TORRENTS_CSV_DOWNLOAD_URL,
    TORRENTS_CSV_DEFAULT_CHECK_INTERVAL,
)
from .api import TorrentsCsvAPIProvider
from .local import TorrentsCsvLocalProvider


class TorrentsCsvSearchProvider(TorrentsCsvBaseProvider):
    """
    Torrent that uses `Torrents.csv <https://torrents-csv.com/>`_ to search
    for torrents, either by using the API or by leveraging a local database.
    """

    def __init__(
        self,
        api_url: str = TORRENT_CSV_API_URL,
        csv_url: str = TORRENTS_CSV_DOWNLOAD_URL,
        download_csv: bool = False,
        csv_path: Optional[str] = None,
        db_path: Optional[str] = None,
        csv_url_check_interval: int = TORRENTS_CSV_DEFAULT_CHECK_INTERVAL,
        **kwargs
    ):
        """
        :param api_url: Torrents.csv API URL.
        :param csv_url: Torrents.csv CSV URL.
        :param download_csv: Whether to download the CSV file.
        :param csv_path: Path to the CSV file.
        :param db_path: Path to the SQLite database file.
        :param csv_url_check_interval: Interval to check for CSV updates.
        """
        super().__init__(**kwargs)
        self.api_url = api_url
        self.csv_url = csv_url
        self.download_csv = download_csv
        self.csv_path = os.path.expanduser(csv_path) if csv_path else None
        self.db_path = os.path.expanduser(db_path) if db_path else None
        self.csv_url_check_interval = csv_url_check_interval

    @property
    def _delegate(self) -> TorrentsCsvBaseProvider:
        """
        :return: The provider to delegate the search to.
        """
        if self.download_csv or self.csv_path or self.db_path:
            return TorrentsCsvLocalProvider(
                download_csv=self.download_csv,
                csv_url=self.csv_url,
                csv_path=self.csv_path,
                db_path=self.db_path,
                csv_url_check_interval=self.csv_url_check_interval,
                enabled=True,
            )

        return TorrentsCsvAPIProvider(api_url=self.api_url, enabled=True)

    @classmethod
    def default_enabled(cls) -> bool:
        """
        This provider is enabled by default.
        """
        return True

    def _search(
        self, query: str, *_, limit: int = 25, page: int = 1, **__
    ) -> List[TorrentSearchResult]:
        """
        Perform a search of torrents using the Torrent.csv API.

        :param query: Query string.
        :param limit: Number of results to return (default: 25).
        :param page: Page number (default: 1).
        """
        results = list(self._delegate.search(query=query, limit=limit, page=page))
        for result in results:
            result.provider = self.provider_name()

        return results


# vim:sw=4:ts=4:et:
