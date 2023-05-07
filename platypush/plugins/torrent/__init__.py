import os
import queue
import random
from typing import List, Optional

import requests
import threading
import time

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


class TorrentPlugin(Plugin):
    """
    Plugin to search and download torrents.

    Requires:

        * **python-libtorrent** (``pip install python-libtorrent``)

    """

    # Wait time in seconds between two torrent transfer checks
    _MONITOR_CHECK_INTERVAL = 3

    default_torrent_ports = [6881, 6891]
    categories = {
        'movies': None,
        'tv': None,
    }

    torrent_state = {}
    transfers = {}
    # noinspection HttpUrlsUsage
    default_popcorn_base_url = 'http://popcorn-time.ga'

    def __init__(
        self,
        download_dir=None,
        torrent_ports=None,
        imdb_key=None,
        popcorn_base_url=default_popcorn_base_url,
        **kwargs,
    ):
        """
        :param download_dir: Directory where the videos/torrents will be downloaded (default: none)
        :type download_dir: str

        :param torrent_ports: Torrent ports to listen on (default: 6881 and 6891)
        :type torrent_ports: list[int]

        :param imdb_key: The IMDb API (https://imdb-api.com/) is used to search for movies and series. Insert your
            IMDb API key if you want support for content search.
        :type imdb_key: str

        :param popcorn_base_url: Custom base URL to use for the PopcornTime API.
        :type popcorn_base_url: str
        """

        super().__init__(**kwargs)

        if torrent_ports is None:
            torrent_ports = []

        for category in self.categories.keys():
            self.categories[category] = getattr(self, 'search_' + category)

        self.imdb_key = imdb_key
        self.imdb_urls = {}
        self.torrent_ports = (
            torrent_ports if torrent_ports else self.default_torrent_ports
        )
        self.download_dir = None
        self._sessions = {}
        self._lt_session = None
        self.popcorn_base_url = popcorn_base_url
        self.torrent_base_urls = {
            'movies': f'{popcorn_base_url}/movie/{{}}',
            'tv': f'{popcorn_base_url}/show/{{}}',
        }

        if imdb_key:
            self.imdb_urls = {
                'movies': f'https://imdb-api.com/API/SearchMovie/{self.imdb_key}/{{}}',
                'tv': f'https://imdb-api.com/API/SearchSeries/{self.imdb_key}/{{}}',
            }

        if download_dir:
            self.download_dir = os.path.abspath(os.path.expanduser(download_dir))

    @action
    def search(self, query, category=None, language=None, *args, **kwargs):
        """
        Perform a search of video torrents.

        :param query: Query string, video name or partial name
        :type query: str

        :param category: Category to search. Supported types: "movies", "tv".
            Default: None (search all categories)
        :type category: str or list

        :param language: Language code for the results - example: "en" (default: None, no filter)
        :type language: str
        """

        assert self.imdb_key, 'No imdb_key specified'
        results = []
        if isinstance(category, str):
            category = [category]

        # noinspection PyCallingNonCallable
        def worker(cat):
            if cat not in self.categories:
                raise RuntimeError(
                    'Unsupported category {}. Supported category: {}'.format(
                        cat, self.categories.keys()
                    )
                )

            self.logger.info('Searching {} torrents for "{}"'.format(cat, query))
            results.extend(
                self.categories[cat](query, *args, language=language, **kwargs)
            )

        workers = [
            threading.Thread(target=worker, kwargs={'cat': category})
            for category in (category or self.categories.keys())
        ]

        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()

        return results

    def _imdb_query(self, query: str, category: str):
        assert self.imdb_key, 'No imdb_key specified'
        imdb_url = self.imdb_urls.get(category)

        assert imdb_url, f'No such category: {category}'
        imdb_url = imdb_url.format(query)
        response = requests.get(imdb_url).json()

        assert not response.get('errorMessage'), response['errorMessage']
        return response.get('results', [])

    def _torrent_search_worker(self, imdb_id: str, category: str, q: queue.Queue):
        base_url = self.torrent_base_urls.get(category)
        assert base_url, f'No such category: {category}'
        try:
            results = requests.get(base_url.format(imdb_id)).json()
            q.put(results)
        except Exception as e:
            q.put(e)

    def _search_torrents(self, query, category):
        imdb_results = self._imdb_query(query, category)
        result_queues = [queue.Queue()] * len(imdb_results)
        workers = [
            threading.Thread(
                target=self._torrent_search_worker,
                kwargs={
                    'imdb_id': imdb_results[i]['id'],
                    'category': category,
                    'q': result_queues[i],
                },
            )
            for i in range(len(imdb_results))
        ]

        results = []
        errors = []

        for worker in workers:
            worker.start()
        for q in result_queues:
            res_ = q.get()
            if isinstance(res_, Exception):
                errors.append(res_)
            else:
                results.append(res_)
        for worker in workers:
            worker.join()

        if errors:
            self.logger.warning(f'Torrent search errors: {[str(e) for e in errors]}')

        return results

    @staticmethod
    def _results_to_movies_response(
        results: List[dict], language: Optional[str] = None
    ):
        return sorted(
            [
                {
                    'imdb_id': result.get('imdb_id'),
                    'type': 'movies',
                    'file': item.get('file'),
                    'title': '{title} [movies][{language}][{quality}]'.format(
                        title=result.get('title'), language=lang, quality=quality
                    ),
                    'duration': int(result.get('runtime') or 0),
                    'year': int(result.get('year') or 0),
                    'synopsis': result.get('synopsis'),
                    'trailer': result.get('trailer'),
                    'genres': result.get('genres', []),
                    'images': result.get('images', []),
                    'rating': result.get('rating', {}),
                    'language': lang,
                    'quality': quality,
                    'size': item.get('size'),
                    'provider': item.get('provider'),
                    'seeds': item.get('seed'),
                    'peers': item.get('peer'),
                    'url': item.get('url'),
                }
                for result in results
                for (lang, items) in (result.get('torrents', {}) or {}).items()
                if not language or language == lang
                for (quality, item) in items.items()
                if quality != '0'
            ],
            key=lambda item: item.get('seeds', 0),
            reverse=True,
        )

    @staticmethod
    def _results_to_tv_response(results: List[dict]):
        return sorted(
            [
                {
                    'imdb_id': result.get('imdb_id'),
                    'tvdb_id': result.get('tvdb_id'),
                    'type': 'tv',
                    'file': item.get('file'),
                    'series': result.get('title'),
                    'title': '{series} [S{season:02d}E{episode:02d}] {title} [tv][{quality}]'.format(
                        series=result.get('title'),
                        season=episode.get('season'),
                        episode=episode.get('episode'),
                        title=episode.get('title'),
                        quality=quality,
                    ),
                    'duration': int(result.get('runtime') or 0),
                    'year': int(result.get('year') or 0),
                    'synopsis': result.get('synopsis'),
                    'overview': episode.get('overview'),
                    'season': episode.get('season'),
                    'episode': episode.get('episode'),
                    'num_seasons': result.get('num_seasons'),
                    'country': result.get('country'),
                    'network': result.get('network'),
                    'status': result.get('status'),
                    'genres': result.get('genres', []),
                    'images': result.get('images', []),
                    'rating': result.get('rating', {}),
                    'quality': quality,
                    'provider': item.get('provider'),
                    'seeds': item.get('seeds'),
                    'peers': item.get('peers'),
                    'url': item.get('url'),
                }
                for result in results
                for episode in result.get('episodes', [])
                for quality, item in (episode.get('torrents', {}) or {}).items()
                if quality != '0'
            ],
            key=lambda item: '{series}.{quality}.{season:02d}.{episode:02d}'.format(
                series=item.get('series'),
                quality=item.get('quality'),
                season=item.get('season'),
                episode=item.get('episode'),
            ),
        )

    def search_movies(self, query, language=None):
        return self._results_to_movies_response(
            self._search_torrents(query, 'movies'), language=language
        )

    def search_tv(self, query, **_):
        return self._results_to_tv_response(self._search_torrents(query, 'tv'))

    def _get_torrent_info(self, torrent, download_dir):
        import libtorrent as lt

        torrent_file = None
        magnet = None
        info = {}
        file_info = {}

        # noinspection HttpUrlsUsage
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
            response = requests.get(torrent, allow_redirects=True)
            torrent_file = os.path.join(download_dir, self._generate_rand_filename())

            with open(torrent_file, 'wb') as f:
                f.write(response.content)
        else:
            torrent_file = os.path.abspath(os.path.expanduser(torrent))
            if not os.path.isfile(torrent_file):
                raise RuntimeError(
                    '{} is not a valid torrent file'.format(torrent_file)
                )

        if torrent_file:
            file_info = lt.torrent_info(torrent_file)
            # noinspection PyArgumentList
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
            self.logger.warning('Exception in torrent event handler: {}'.format(str(e)))
            self.logger.exception(e)

    def _torrent_monitor(self, torrent, transfer, download_dir, event_hndl, is_media):
        def thread():
            files = []
            last_status = None
            download_started = False
            metadata_downloaded = False

            while not transfer.is_finished():
                if torrent not in self.transfers:
                    self.logger.info(
                        'Torrent {} has been stopped and removed'.format(torrent)
                    )
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

                        # noinspection PyProtectedMember
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

        # noinspection PyArgumentList
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
            self.logger.info(
                'A torrent session is already running for {}'.format(torrent)
            )
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
            'Downloading "{}" to "{}" from [{}]'.format(
                info['name'], download_dir, torrent
            )
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
            return None, "No transfer in progress for {}".format(torrent)

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

        if torrent not in self.transfers:
            return None, "No transfer in progress for {}".format(torrent)

        self.transfers[torrent].resume()

    @action
    def remove(self, torrent):
        """
        Stops and removes a torrent transfer.

        :param torrent: Torrent URL as returned from `get_status()`
        :type torrent: str
        """

        if torrent not in self.transfers:
            return None, "No transfer in progress for {}".format(torrent)

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
