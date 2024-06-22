import datetime as dt
import os
import pathlib
import re
import stat
import subprocess
import time
from threading import RLock
from typing import List, Optional
from urllib.parse import quote_plus

import requests
from sqlalchemy import create_engine, text

from platypush.config import Config
from platypush.context import Variable

from .._model import TorrentSearchResult
from ._base import TorrentsCsvBaseProvider
from ._constants import TORRENTS_CSV_URL_LAST_CHECKED_VAR

SQL_INIT_TEMPLATE = """
create table torrent_tmp (
  infohash text primary key,
  name text not null,
  size_bytes integer not null,
  created_unix integer(4) not null,
  seeders integer not null,
  leechers integer not null,
  completed integer not null,
  scraped_date integer(4) not null,
  published integer(4) not null
);

.separator ,
.import --skip 1 '{csv_file}' torrent_tmp

create index idx_name on torrent_tmp(lower(name));
create index idx_seeders on torrent_tmp(seeders);
create index idx_created_unix on torrent_tmp(created_unix);

drop table if exists torrent;
alter table torrent_tmp rename to torrent;
"""


class TorrentsCsvLocalProvider(TorrentsCsvBaseProvider):
    """
    This class is responsible for managing a local checkout of the torrents-csv
    dataset.
    """

    def __init__(
        self,
        download_csv: bool,
        csv_url: str,
        csv_url_check_interval: int,
        csv_path: Optional[str] = None,
        db_path: Optional[str] = None,
        **kwargs,
    ):
        """
        Note that at least one among ``download_csv``, ``csv_path`` and ``db_path``
        should be provided.

        :param download_csv: If True then the CSV file will be downloaded from the
            specified ``csv_url``.
        :param csv_url: The URL from which the CSV file will be downloaded.
        :param csv_url_check_interval: The interval in seconds after which the CSV
            should be checked for updates.
        :param csv_path: The path to the CSV file. If not provided, and download_csv
            is set to True, then the CSV file will be downloaded to
            ``<WORKDIR>/torrent/torrents.csv``.
        :param db_path: The path to the SQLite database. If not provided, and
            ``csv_path`` or ``download_csv`` are set, then the database will be created
            from a local copy of the CSV file.
        """
        super().__init__(**kwargs)
        assert (
            download_csv or csv_path or db_path
        ), 'You must provide either download_csv, csv_path or db_path'

        self._init_csv_lock = RLock()
        self._init_db_lock = RLock()
        self._csv_url_check_interval = csv_url_check_interval

        if download_csv:
            csv_path = (
                os.path.expanduser(csv_path)
                if csv_path
                else os.path.join(Config.get_workdir(), 'torrent', 'torrents.csv')
            )

            with self._init_csv_lock:
                self._download_csv(csv_url=csv_url, csv_path=csv_path)

        if csv_path:
            db_path = (
                os.path.expanduser(db_path)
                if db_path
                else os.path.join(os.path.dirname(csv_path), 'torrents.db')
            )

            with self._init_db_lock:
                self._build_db(csv_path=csv_path, db_path=db_path)

        assert db_path, 'No download_csv, csv_path or db_path provided'
        assert os.path.isfile(db_path), f'Invalid db_path: {db_path}'
        self.db_path = db_path

    def _get_engine(self):
        return create_engine(
            'sqlite:///' + ('/'.join(map(quote_plus, self.db_path.split(os.path.sep))))
        )

    def _download_csv(self, csv_url: str, csv_path: str):
        if not self._should_download_csv(
            csv_url=csv_url,
            csv_path=csv_path,
            csv_url_check_interval=self._csv_url_check_interval,
        ):
            return

        self.logger.info(
            'Downloading the torrents CSV file from %s to %s', csv_url, csv_path
        )

        response = requests.get(csv_url, stream=True, timeout=60)
        response.raise_for_status()
        size = int(response.headers.get('Content-Length', 0))
        torrents_csv_dir = os.path.dirname(csv_path)
        pathlib.Path(torrents_csv_dir).mkdir(parents=True, exist_ok=True)

        with open(csv_path, 'wb') as f:
            written = 0

            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                written += len(chunk)
                if size:
                    percent = 100.0 * written / size
                    prev_percent = max(0, 100.0 * (written - len(chunk)) / size)
                    if round(percent / 5) > round(prev_percent / 5):
                        self.logger.info('... %.2f%%\r', percent)

        self.logger.info('Downloaded the torrents CSV file to %s', csv_path)

    def _build_db(self, csv_path: str, db_path: str):
        if not self._should_update_db(csv_path, db_path):
            return

        self.logger.info(
            'Refreshing SQLite database %s from CSV file %s', db_path, csv_path
        )

        db_dir = os.path.dirname(db_path)
        pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)

        with subprocess.Popen(
            ['sqlite3', db_path], stdin=subprocess.PIPE, text=True
        ) as proc:
            proc.communicate(SQL_INIT_TEMPLATE.format(csv_file=csv_path))

        self.logger.info(
            'Refreshed SQLite database %s from CSV file %s: ready to search',
            db_path,
            csv_path,
        )

    @staticmethod
    def _should_update_db(csv_path: str, db_path: str) -> bool:
        if not os.path.isfile(csv_path):
            return False

        if not os.path.isfile(db_path):
            return True

        return os.stat(db_path)[stat.ST_MTIME] < os.stat(csv_path)[stat.ST_MTIME]

    def _should_download_csv(
        self, csv_url: str, csv_path: str, csv_url_check_interval: int
    ) -> bool:
        if not os.path.isfile(csv_path):
            self.logger.info('CSV file %s not found, downloading it', csv_path)
            return True

        if not self._should_check_csv_url(csv_url_check_interval):
            self.logger.debug('No need to check the CSV URL %s', csv_url)
            return False

        request = requests.head(csv_url, timeout=10)
        request.raise_for_status()
        last_modified_hdr = request.headers.get('Last-Modified')
        Variable(TORRENTS_CSV_URL_LAST_CHECKED_VAR).set(time.time())

        if not last_modified_hdr:
            self.logger.debug(
                "No Last-Modified header found in the CSV URL, can't compare thus downloading"
            )
            return True

        return (
            time.mktime(time.strptime(last_modified_hdr, '%a, %d %b %Y %H:%M:%S %Z'))
            > os.stat(csv_path)[stat.ST_MTIME]
        )

    @staticmethod
    def _should_check_csv_url(csv_url_check_interval: int) -> bool:
        last_checked = round(
            float(Variable(TORRENTS_CSV_URL_LAST_CHECKED_VAR).get() or 0)
        )
        return bool(
            csv_url_check_interval
            and time.time() - last_checked > csv_url_check_interval
        )

    def _search(
        self, query: str, *_, limit: int, page: int, **__
    ) -> List[TorrentSearchResult]:
        self.logger.debug(
            "Searching for %r on %s, limit=%d, page=%d",
            query,
            self.db_path,
            limit,
            page,
        )

        tokens = re.split(r'[^\w]', query.lower())
        where = ' and '.join(
            f'lower(name) like :token{i}' for i, _ in enumerate(tokens)
        )
        tokens = {f'token{i}': f'%{token}%' for i, token in enumerate(tokens)}

        with self._get_engine().connect() as conn:
            self.logger.debug('Connected to the database: %s', conn.engine.url)
            results = conn.execute(
                text(
                    f"""
                    select infohash, name, size_bytes, seeders, leechers, created_unix
                    from torrent
                    where {where}
                    order by seeders desc, created_unix desc
                    limit :limit
                    offset :offset
                    """
                ),
                {
                    **tokens,
                    'limit': max(int(limit), 0),
                    'offset': max(int(limit * (page - 1)), 0),
                },
            ).all()

        self.logger.debug('Found %d results', len(results))
        return [
            TorrentSearchResult(
                title=result[1],
                url=self._to_magnet(
                    info_hash=result[0],
                    torrent_name=result[1],
                ),
                size=result[2],
                seeds=int(result[3] or 0),
                peers=int(result[4] or 0),
                created_at=(
                    dt.datetime.fromtimestamp(result[5]).replace(tzinfo=dt.timezone.utc)
                    if result[5]
                    else None
                ),
            )
            for result in results
        ]
