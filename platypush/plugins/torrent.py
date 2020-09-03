import os
import random
import requests
import threading
import time

from platypush.context import get_bus
from platypush.plugins import Plugin, action
from platypush.message.event.torrent import \
    TorrentDownloadStartEvent, TorrentDownloadedMetadataEvent, TorrentStateChangeEvent, \
    TorrentDownloadProgressEvent, TorrentDownloadCompletedEvent, TorrentDownloadStopEvent, \
    TorrentPausedEvent, TorrentResumedEvent, TorrentQueuedEvent


class TorrentPlugin(Plugin):
    """
    Plugin to search and download torrents.

    Requires:

        * **python-libtorrent** (``pip install git+https://github.com/arvidn/libtorrent``)
        * **requests** (``pip install requests``) [optional] for torrent info URL download
    """

    # Wait time in seconds between two torrent transfer checks
    _MONITOR_CHECK_INTERVAL = 3

    default_torrent_ports = [6881, 6891]
    categories = {
        'movies': None,
        'tv': None,
        # 'anime': None,
    }

    torrent_state = {}
    transfers = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }

    def __init__(self, download_dir=None, torrent_ports=None, **kwargs):
        """
        :param download_dir: Directory where the videos/torrents will be downloaded (default: none)
        :type download_dir: str

        :param torrent_ports: Torrent ports to listen on (default: 6881 and 6891)
        :type torrent_ports: list[int]
        """

        super().__init__(**kwargs)

        if torrent_ports is None:
            torrent_ports = []

        for category in self.categories.keys():
            self.categories[category] = getattr(self, 'search_' + category)

        self.torrent_ports = torrent_ports if torrent_ports else self.default_torrent_ports
        self.download_dir = None
        self._sessions = {}

        if download_dir:
            self.download_dir = os.path.abspath(os.path.expanduser(download_dir))

    # noinspection PyIncorrectDocstring
    @action
    def search(self, query, category=None, *args, **kwargs):
        """
        Perform a search of video torrents.

        :param query: Query string, video name or partial name
        :type query: str

        :param category: Category to search. Supported types: "movies", "tv", "anime".
            Default: None (search all categories)
        :type category: str or list

        :param language: Language code for the results - example: "en" (default: None, no filter)
        :type language: str
        """

        if isinstance(category, str):
            category = [category]

        results = {
            category: []
            for category in (category or self.categories.keys())
        }

        # noinspection PyCallingNonCallable
        def worker(cat):
            if cat not in self.categories:
                raise RuntimeError('Unsupported category {}. Supported category: {}'.
                                   format(cat, self.categories.keys()))

            self.logger.info('Searching {} torrents for "{}"'.format(cat, query))
            results[cat] = self.categories[cat](query, *args, **kwargs)

        workers = [
            threading.Thread(target=worker, kwargs={'cat': category})
            for category in (category or self.categories.keys())
        ]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        ret = []
        for (category, items) in results.items():
            ret += items
        return ret

    def search_movies(self, query, language=None):
        response = requests.get(
            'https://movies-v2.api-fetch.sh/movies/1', params={
                'sort': 'relevance',
                'keywords': query,
            }, headers=self.headers
        ).json()

        return sorted([
            {
                'imdb_id': result.get('imdb_id'),
                'type': 'movies',
                'title': '{title} [movies][{language}][{quality}]'.format(
                    title=result.get('title'), language=lang, quality=quality),
                'year': result.get('year'),
                'synopsis': result.get('synopsis'),
                'trailer': result.get('trailer'),
                'language': lang,
                'quality': quality,
                'size': item.get('size'),
                'seeds': item.get('seed'),
                'peers': item.get('peer'),
                'url': item.get('url'),
            }
            for result in (response or [])
            for (lang, items) in result.get('torrents', {}).items()
            if not language or language == lang
            for (quality, item) in items.items()
        ], key=lambda _: _.get('seeds'), reverse=True)

    def search_tv(self, query):
        shows = requests.get(
            'https://tv-v2.api-fetch.sh/shows/1', params={
                'sort': 'relevance',
                'keywords': query,
            }, headers=self.headers
        ).json()

        results = []

        for show in shows:
            show = requests.get(
                'https://tv-v2.api-fetch.website/show/' + show.get('_id'),
                headers=self.headers
            ).json()

            results.extend(sorted([
                {
                    'imdb_id': show.get('imdb_id'),
                    'tvdb_id': show.get('tvdb_id'),
                    'type': 'tv',
                    'title': '[{show}][s{season}e{episode:02d}] {title} [tv][{quality}]'.format(
                        show=show.get('title'), season=episode.get('season', 0),
                        episode=episode.get('episode', 0), title=episode.get('title'), quality=quality),
                    'season': episode.get('season'),
                    'episode': episode.get('episode'),
                    'year': show.get('year'),
                    'first_aired': episode.get('first_aired'),
                    'quality': quality,
                    'num_seasons': show.get('num_seasons'),
                    'status': show.get('status'),
                    'network': show.get('network'),
                    'country': show.get('country'),
                    'show_synopsis': show.get('synopsys'),
                    'synopsis': episode.get('overview'),
                    'provider': torrent.get('provider'),
                    'seeds': torrent.get('seeds'),
                    'peers': torrent.get('peers'),
                    'url': torrent.get('url'),
                }
                for episode in show.get('episodes', [])
                for quality, torrent in episode.get('torrents', {}).items()
                if quality != '0'
            ], key=lambda _: int(_.get('season')*100) + int(_.get('episode'))))

        return results

    def search_anime(self, query):
        shows = requests.get(
            'https://popcorn-api.io/animes/1', params={
                'sort': 'relevance',
                'keywords': query,
            }, headers=self.headers
        ).json()

        results = []

        for show in shows:
            show = requests.get('https://anime.api-fetch.website/anime/' + show.get('_id'),
                                headers=self.headers).json()

            results.extend(sorted([
                {
                    'tvdb_id': episode.get('tvdb_id'),
                    'type': 'anime',
                    'title': '[{show}][s{season}e{episode:02d}] {title} [anime][{quality}]'.format(
                        show=show.get('title'), season=int(episode.get('season', 0)),
                        episode=int(episode.get('episode', 0)), title=episode.get('title'), quality=quality),
                    'season': episode.get('season'),
                    'episode': episode.get('episode'),
                    'year': show.get('year'),
                    'quality': quality,
                    'num_seasons': show.get('num_seasons'),
                    'status': show.get('status'),
                    'show_synopsis': show.get('synopsys'),
                    'synopsis': episode.get('overview'),
                    'seeds': torrent.get('seeds'),
                    'peers': torrent.get('peers'),
                    'url': torrent.get('url'),
                }
                for episode in show.get('episodes', [])
                for quality, torrent in episode.get('torrents', {}).items()
                if quality != '0'
            ], key=lambda _: int(_.get('season')*100) + int(_.get('episode'))))

        return results

    # noinspection PyArgumentList
    def _get_torrent_info(self, torrent, download_dir):
        import libtorrent as lt

        torrent_file = None
        magnet = None
        info = {}
        file_info = {}

        if torrent.startswith('magnet:?'):
            magnet = torrent
            magnet_info = lt.parse_magnet_uri(magnet)
            info = {
                'name': magnet_info.name,
                'url': magnet,
                'magnet': magnet,
                'trackers': magnet_info.trackers,
                'save_path': download_dir,
            }
        elif torrent.startswith('http://') or torrent.startswith('https://'):
            response = requests.get(torrent, headers=self.headers, allow_redirects=True)
            torrent_file = os.path.join(download_dir, self._generate_rand_filename())

            with open(torrent_file, 'wb') as f:
                f.write(response.content)
        else:
            torrent_file = os.path.abspath(os.path.expanduser(torrent))
            if not os.path.isfile(torrent_file):
                raise RuntimeError('{} is not a valid torrent file'.format(torrent_file))

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
                    self.logger.info('Torrent {} has been stopped and removed'.format(torrent))
                    self._fire_event(TorrentDownloadStopEvent(url=torrent), event_hndl)
                    break

                status = transfer.status()
                torrent_file = transfer.torrent_file()

                if torrent_file:
                    self.torrent_state[torrent]['size'] = torrent_file.total_size()
                    files = [os.path.join(
                        download_dir,
                        torrent_file.files().file_path(i))
                        for i in range(0, torrent_file.files().num_files())
                    ]

                    if is_media:
                        from platypush.plugins.media import MediaPlugin
                        # noinspection PyProtectedMember
                        files = [f for f in files if MediaPlugin._is_video_file(f)]

                self.torrent_state[torrent]['download_rate'] = status.download_rate
                self.torrent_state[torrent]['name'] = status.name
                self.torrent_state[torrent]['num_peers'] = status.num_peers
                self.torrent_state[torrent]['paused'] = status.paused
                self.torrent_state[torrent]['progress'] = round(100 * status.progress, 2)
                self.torrent_state[torrent]['state'] = status.state.name
                self.torrent_state[torrent]['title'] = status.name
                self.torrent_state[torrent]['torrent'] = torrent
                self.torrent_state[torrent]['upload_rate'] = status.upload_rate
                self.torrent_state[torrent]['url'] = torrent
                self.torrent_state[torrent]['files'] = files

                if transfer.has_metadata() and not metadata_downloaded:
                    self._fire_event(TorrentDownloadedMetadataEvent(**self.torrent_state[torrent]), event_hndl)
                    metadata_downloaded = True

                if status.state == status.downloading and not download_started:
                    self._fire_event(TorrentDownloadStartEvent(**self.torrent_state[torrent]), event_hndl)
                    download_started = True

                if last_status and status.progress != last_status.progress:
                    self._fire_event(TorrentDownloadProgressEvent(**self.torrent_state[torrent]), event_hndl)

                if not last_status or status.state != last_status.state:
                    self._fire_event(TorrentStateChangeEvent(**self.torrent_state[torrent]), event_hndl)

                if last_status and status.paused != last_status.paused:
                    if status.paused:
                        self._fire_event(TorrentPausedEvent(**self.torrent_state[torrent]), event_hndl)
                    else:
                        self._fire_event(TorrentResumedEvent(**self.torrent_state[torrent]), event_hndl)

                last_status = status
                time.sleep(self._MONITOR_CHECK_INTERVAL)

            if transfer and transfer.is_finished():
                self._fire_event(TorrentDownloadCompletedEvent(**self.torrent_state[torrent]), event_hndl)

            self.remove(torrent)
            return files

        return thread

    @action
    def download(self, torrent, download_dir=None, _async=False, event_hndl=None, is_media=False):
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
        info, file_info, torrent_file, magnet = self._get_torrent_info(torrent, download_dir)

        if torrent in self._sessions:
            self.logger.info('A torrent session is already running for {}'.format(torrent))
            return self.torrent_state.get(torrent, {})

        # noinspection PyArgumentList
        session = lt.session()
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
        }

        self._fire_event(TorrentQueuedEvent(url=torrent), event_hndl)
        self.logger.info('Downloading "{}" to "{}" from [{}]'.format(info['name'], download_dir, torrent))
        monitor_thread = self._torrent_monitor(torrent=torrent, transfer=transfer, download_dir=download_dir,
                                               event_hndl=event_hndl, is_media=is_media)

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
        for i in range(0, length):
            name += hex(random.randint(0, 15))[2:].upper()
        return name + '.torrent'


# vim:sw=4:ts=4:et:
