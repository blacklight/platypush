import inspect
import os
import pathlib
import random
import threading
import time
from typing import Dict, Iterable, Optional, Union

import requests

from platypush.context import get_bus
from platypush.plugins import Plugin, action
from platypush.message.event.torrent import (
    TorrentDownloadStartEvent,
    TorrentDownloadedMetadataEvent,
    TorrentStateChangeEvent,
    TorrentDownloadProgressEvent,
    TorrentDownloadCompletedEvent,
    TorrentDownloadStopEvent,
    TorrentPausedEvent,
    TorrentResumedEvent,
    TorrentQueuedEvent,
)
from platypush.utils import get_default_downloads_dir

from . import _search as search_module
from ._search import TorrentSearchProvider


class TorrentPlugin(Plugin):
    """
    Plugin to search and download torrents.

    Search
    ------

    You can search for torrents using the :meth:`search` method. The method will
    use the search providers configured in the ``search_providers`` attribute of
    the plugin configuration. Currently supported search providers:

        * ``popcorntime``:
            :class:`platypush.plugins.torrent._search.PopcornTimeSearchProvider`
        * ``torrents.csv``:
            :class:`platypush.plugins.torrent._search.TorrentsCsvSearchProvider`

    ``torrents.csv`` will be enabled by default unless you explicitly disable
    it. ``torrents.csv`` also supports both:

        * A remote API via the ``api_url`` attribute (default:
           `https://torrents-csv.com/service``). You can also run your own API
           server by following the instructions at `heretic/torrents-csv-server
           <https://git.torrents-csv.com/heretic/torrents-csv-server>`_.

        * A local checkout of the ``torrents.csv`` file. Clone the
          `heretic/torrents-csv-data
          <https://git.torrents-csv.com/heretic/torrents-csv-data>`_ and provide
          the path to the ``torrents.csv`` file in the ``csv_file`` attribute.

        * A local checkout of the ``torrents.db`` file built from the
          ``torrents.csv`` file. Follow the instructions at
          `heretic/torrents-csv-data
          <https://git.torrents-csv.com/heretic/torrents-csv-data>`_ on how to
          build the ``torrents.db`` file from the ``torrents.csv`` file.

    If you opt for a local checkout of the ``torrents.csv`` file, then
    Platypush will build the SQLite database from the CSV file for you - no need
    to use external services. This however means that the first search will be
    slower as the database is being built. Subsequent searches will be faster,
    unless you modify the CSV file - in this case, an updated database will be
    built from the latest CSV file.

    You can also specify the ``download_csv`` property in the configuration. In
    this case, Platypush will automatically download the latest ``torrents.csv``
    file locally and build the SQLite database from it. On startup, Platypush
    will check if either the local or remote CSV file has been updated, and
    rebuild the database if necessary.

    ``popcorntime`` will be disabled by default unless you explicitly enable it.
    That's because, at the time of writing (June 2024), there are no publicly
    available PopcornTime API servers. You can run your own PopcornTime API
    server by following the instructions at `popcorn-time-ru/popcorn-ru
    <https://github.com/popcorn-time-ru/popcorn-ru>`_.

    Configuration example:

    .. code-block:: yaml

        torrent:
          # ...

          search_providers:
            torrents.csv:
              # Default: True
              # enabled: true
              # Base URL of the torrents.csv API.
              api_url: https://torrents-csv.com/service

              # Alternatively, you can also use a local checkout of the
              # torrents.csv file.
              # csv_file: /path/to/torrents.csv

              # Or a manually built SQLite database from the torrents.csv file.
              # db_file: /path/to/torrents.db

              # Or automatically download the latest torrents.csv file.
              # download_csv: true
            popcorn_time:
              # Default: false
              # enabled: false
              # Required: PopcornTime API base URL.
              api_url: https://popcorntime.app

    """

    _http_timeout = 20

    # Wait time in seconds between two torrent transfer checks
    _MONITOR_CHECK_INTERVAL = 3

    default_torrent_ports = (6881, 6891)
    torrent_state = {}
    transfers = {}

    def __init__(
        self,
        download_dir: Optional[str] = None,
        torrent_ports: Iterable[int] = default_torrent_ports,
        search_providers: Optional[
            Union[Dict[str, dict], Iterable[TorrentSearchProvider]]
        ] = None,
        **kwargs,
    ):
        """
        :param download_dir: Directory where the videos/torrents will be
            downloaded (default: ``~/Downloads``).
        :param torrent_ports: Torrent ports to listen on (default: 6881 and 6891)
        :param search_providers: List of search providers to use.
        """
        super().__init__(**kwargs)

        self.torrent_ports = torrent_ports
        self.download_dir = os.path.abspath(
            os.path.expanduser(download_dir or get_default_downloads_dir())
        )

        self._search_providers = self._load_search_providers(search_providers)
        self.logger.info(
            'Loaded search providers: %s',
            [provider.provider_name() for provider in self._search_providers],
        )

        self._sessions = {}
        self._lt_session = None
        pathlib.Path(self.download_dir).mkdir(parents=True, exist_ok=True)

    def _load_search_providers(
        self,
        search_providers: Optional[
            Union[Dict[str, dict], Iterable[TorrentSearchProvider]]
        ],
    ) -> Iterable[TorrentSearchProvider]:
        provider_classes = {
            cls.provider_name(): cls
            for _, cls in inspect.getmembers(search_module, inspect.isclass)
            if issubclass(cls, TorrentSearchProvider) and cls != TorrentSearchProvider
        }

        if not search_providers:
            return [
                provider()
                for provider in provider_classes.values()
                if provider.default_enabled()
            ]

        parsed_providers = []
        if isinstance(search_providers, dict):
            providers_dict = {}

            # Configure the search providers explicitly passed in the configuration
            for provider_name, provider_config in search_providers.items():
                if provider_name not in provider_classes:
                    self.logger.warning(
                        'Unsupported search provider %s. Supported providers: %s',
                        provider_name,
                        list(provider_classes.keys()),
                    )
                    continue

                provider_class = provider_classes[provider_name]
                providers_dict[provider_name] = provider_class(
                    **{'enabled': True, **provider_config}
                )

            # Enable the search providers that have `default_enabled` set to True
            # and that are not explicitly disabled
            for provider_name, provider in provider_classes.items():
                if provider.default_enabled() and provider_name not in search_providers:
                    providers_dict[provider_name] = provider()

            parsed_providers = list(providers_dict.values())
        else:
            parsed_providers = search_providers

        assert all(
            isinstance(provider, TorrentSearchProvider) for provider in parsed_providers
        ), 'All search providers must be instances of TorrentSearchProvider'

        return parsed_providers

    @action
    def search(
        self,
        query: str,
        *args,
        providers: Optional[Union[str, Iterable[str]]] = None,
        limit: int = 25,
        page: int = 1,
        **filters,
    ):
        """
        Perform a search of video torrents.

        :param query: Query string, video name or partial name
        :param providers: Override the default search providers by specifying
            the provider names to use for this search.
        :param filters: Additional filters to apply to the search, depending on
            what the configured search providers support. For example,
            ``category`` and ``language`` are supported by the PopcornTime.
        :param limit: Maximum number of results to return (default: 25).
        :param page: Page number (default: 1).
        :return: .. schema:: torrent.TorrentResultSchema(many=True)
        """
        results = []

        def worker(provider: TorrentSearchProvider):
            self.logger.debug(
                'Searching torrents on provider %s, query: %s',
                provider.provider_name(),
                query,
            )
            results.extend(
                provider.search(query, *args, limit=limit, page=page, **filters)
            )

        if providers:
            providers = [providers] if isinstance(providers, str) else providers
            search_providers = [
                provider
                for provider in self._search_providers
                if provider.provider_name() in providers
            ]
        else:
            search_providers = self._search_providers

        if not search_providers:
            self.logger.warning('No search providers enabled')
            return []

        workers = [
            threading.Thread(target=worker, kwargs={'provider': provider})
            for provider in search_providers
        ]

        for wrk in workers:
            wrk.start()
        for wrk in workers:
            wrk.join()

        return [result.to_dict() for result in results]

    def _get_torrent_info(self, torrent, download_dir):
        import libtorrent as lt

        torrent_file = None
        magnet = None
        info = {}
        file_info = {}

        if torrent.startswith('magnet:?'):
            magnet = torrent
            magnet_info = lt.parse_magnet_uri(magnet)
            if isinstance(magnet_info, dict):
                info = {
                    'name': magnet_info.get('name'),
                    'url': magnet,
                    'magnet': magnet,
                    'trackers': magnet_info.get('trackers', []),
                    'save_path': download_dir,
                }
            else:
                info = {
                    'name': magnet_info.name,
                    'url': magnet,
                    'magnet': magnet,
                    'trackers': magnet_info.trackers,
                    'save_path': download_dir,
                }
        elif torrent.startswith('http://') or torrent.startswith('https://'):
            response = requests.get(
                torrent, timeout=self._http_timeout, allow_redirects=True
            )
            torrent_file = os.path.join(download_dir, self._generate_rand_filename())

            with open(torrent_file, 'wb') as f:
                f.write(response.content)
        else:
            torrent_file = os.path.abspath(os.path.expanduser(torrent))
            if not os.path.isfile(torrent_file):
                raise RuntimeError(f'{torrent_file} is not a valid torrent file')

        if torrent_file:
            file_info = lt.torrent_info(torrent_file)
            info = {
                'name': file_info.name(),
                'url': torrent,
                'trackers': [t.url for t in list(file_info.trackers())],
                'save_path': download_dir,
            }

        return info, file_info, torrent_file, magnet

    def _fire_event(self, event, event_hndl):
        bus = get_bus()
        bus.post(event)

        try:
            if event_hndl:
                event_hndl(event)
        except Exception as e:
            self.logger.warning('Exception in torrent event handler: %s', e)
            self.logger.exception(e)

    def _torrent_monitor(self, torrent, transfer, download_dir, event_hndl, is_media):
        def thread():
            files = []
            last_status = None
            download_started = False
            metadata_downloaded = False

            while not transfer.is_finished():
                if torrent not in self.transfers:
                    self.logger.info('Torrent %s has been stopped and removed', torrent)
                    self._fire_event(TorrentDownloadStopEvent(url=torrent), event_hndl)
                    break

                status = transfer.status()
                torrent_file = transfer.torrent_file()

                if torrent_file:
                    self.torrent_state[torrent]['size'] = torrent_file.total_size()
                    files = [
                        os.path.join(download_dir, torrent_file.files().file_path(i))
                        for i in range(0, torrent_file.files().num_files())
                    ]

                    if is_media:
                        from platypush.plugins.media import MediaPlugin

                        files = [f for f in files if MediaPlugin.is_video_file(f)]

                self.torrent_state[torrent]['download_rate'] = status.download_rate
                self.torrent_state[torrent]['name'] = status.name
                self.torrent_state[torrent]['num_peers'] = status.num_peers
                self.torrent_state[torrent]['paused'] = status.paused
                self.torrent_state[torrent]['progress'] = round(
                    100 * status.progress, 2
                )
                self.torrent_state[torrent]['state'] = status.state.name
                self.torrent_state[torrent]['title'] = status.name
                self.torrent_state[torrent]['torrent'] = torrent
                self.torrent_state[torrent]['upload_rate'] = status.upload_rate
                self.torrent_state[torrent]['url'] = torrent
                self.torrent_state[torrent]['files'] = files

                if transfer.has_metadata() and not metadata_downloaded:
                    self._fire_event(
                        TorrentDownloadedMetadataEvent(**self.torrent_state[torrent]),
                        event_hndl,
                    )
                    metadata_downloaded = True

                if status.state == status.downloading and not download_started:
                    self._fire_event(
                        TorrentDownloadStartEvent(**self.torrent_state[torrent]),
                        event_hndl,
                    )
                    download_started = True

                if last_status and status.progress != last_status.progress:
                    self._fire_event(
                        TorrentDownloadProgressEvent(**self.torrent_state[torrent]),
                        event_hndl,
                    )

                if not last_status or status.state != last_status.state:
                    self._fire_event(
                        TorrentStateChangeEvent(**self.torrent_state[torrent]),
                        event_hndl,
                    )

                if last_status and status.paused != last_status.paused:
                    if status.paused:
                        self._fire_event(
                            TorrentPausedEvent(**self.torrent_state[torrent]),
                            event_hndl,
                        )
                    else:
                        self._fire_event(
                            TorrentResumedEvent(**self.torrent_state[torrent]),
                            event_hndl,
                        )

                last_status = status
                time.sleep(self._MONITOR_CHECK_INTERVAL)

            if transfer and transfer.is_finished():
                self._fire_event(
                    TorrentDownloadCompletedEvent(**self.torrent_state[torrent]),
                    event_hndl,
                )

            self.remove(torrent)
            return files

        return thread

    def _get_session(self):
        if self._lt_session:
            return self._lt_session

        import libtorrent as lt

        self._lt_session = lt.session()
        return self._lt_session

    @action
    def download(
        self, torrent, download_dir=None, _async=False, event_hndl=None, is_media=False
    ):
        """
        Download a torrent.

        :param torrent: Torrent to download. Supported formats:

            * Magnet URLs
            * Torrent URLs
            * Local torrent file

        :type torrent: str

        :param download_dir: Directory to download, overrides the default download_dir attribute (default: None)
        :type download_dir: str

        :param _async: If true then the method will add the torrent to the transfer and then return. Updates on
            the download status should be retrieved either by listening to torrent events or registering the
            event handler. If false (default) then the method will exit only when the torrent download is complete.
        :type _async: bool

        :param event_hndl: A function that takes an event object as argument and is invoked upon a new torrent event
            (download started, progressing, completed etc.)
        :type event_hndl: function

        :param is_media: Set it to true if you're downloading a media file that you'd like to stream as soon as the
            first chunks are available. If so, then the events and the status method will only include media files
        :type is_media: bool
        """

        if torrent in self.torrent_state and torrent in self.transfers:
            return self.torrent_state[torrent]

        import libtorrent as lt

        if not download_dir:
            if self.download_dir:
                download_dir = self.download_dir
            else:
                raise RuntimeError('download_dir not specified')

        download_dir = os.path.abspath(os.path.expanduser(download_dir))
        os.makedirs(download_dir, exist_ok=True)
        info, file_info, torrent_file, magnet = self._get_torrent_info(
            torrent, download_dir
        )

        if torrent in self._sessions:
            self.logger.info('A torrent session is already running for %s', torrent)
            return self.torrent_state.get(torrent, {})

        session = self._get_session()
        session.listen_on(*self.torrent_ports)
        self._sessions[torrent] = session

        params = {
            'save_path': download_dir,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        }

        if magnet:
            transfer = lt.add_magnet_uri(session, magnet, params)
        else:
            params['ti'] = file_info
            transfer = session.add_torrent(params)

        self.transfers[torrent] = transfer
        self.torrent_state[torrent] = {
            'url': torrent,
            'title': transfer.status().name,
            'trackers': info['trackers'],
            'save_path': download_dir,
            'torrent_file': torrent_file,
        }

        self._fire_event(TorrentQueuedEvent(url=torrent), event_hndl)
        self.logger.info(
            'Downloading "%s" to "%s" from [%s]', info['name'], download_dir, torrent
        )
        monitor_thread = self._torrent_monitor(
            torrent=torrent,
            transfer=transfer,
            download_dir=download_dir,
            event_hndl=event_hndl,
            is_media=is_media,
        )

        if not _async:
            return monitor_thread()

        threading.Thread(target=monitor_thread).start()
        return self.torrent_state[torrent]

    @action
    def status(self, torrent=None):
        """
        Get the status of the current transfers.

        :param torrent: Torrent path, URL or magnet URI whose status will be retrieve (default: None, retrieve all
            current transfers)
        :type torrent: str

        :returns: A dictionary in the format torrent_url -> status
        """

        if torrent:
            return self.torrent_state.get(torrent)
        return self.torrent_state

    @action
    def pause(self, torrent):
        """
        Pause/resume a torrent transfer.

        :param torrent: Torrent URL as returned from `get_status()`
        :type torrent: str
        """

        if torrent not in self.transfers:
            return None, f"No transfer in progress for {torrent}"

        if self.torrent_state[torrent].get('paused', False):
            self.transfers[torrent].resume()
        else:
            self.transfers[torrent].pause()

        return self.torrent_state[torrent]

    @action
    def resume(self, torrent):
        """
        Resume a torrent transfer.

        :param torrent: Torrent URL as returned from `get_status()`
        :type torrent: str
        """

        assert torrent in self.transfers, f"No transfer in progress for {torrent}"
        self.transfers[torrent].resume()

    @action
    def remove(self, torrent):
        """
        Stops and removes a torrent transfer.

        :param torrent: Torrent URL as returned from `get_status()`
        :type torrent: str
        """

        if not self.transfers.get(torrent):
            self.logger.info('No transfer in progress for %s', torrent)
            return

        self.transfers[torrent].pause()
        del self.torrent_state[torrent]
        del self.transfers[torrent]
        if torrent in self._sessions:
            del self._sessions[torrent]

    @action
    def quit(self):
        """
        Quits all the transfers and the active session
        """
        transfers = self.transfers.copy()
        for torrent in transfers:
            self.remove(torrent)

    @staticmethod
    def _generate_rand_filename(length=16):
        name = ''
        for _ in range(0, length):
            name += hex(random.randint(0, 15))[2:].upper()
        return name + '.torrent'


# vim:sw=4:ts=4:et:
