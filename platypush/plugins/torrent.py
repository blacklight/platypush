import json
import os
import random
import threading
import time

import urllib.request
import urllib.parse

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
    supported_categories = {
        'movies': 'https://movies-v2.api-fetch.website/movies/1',
        'tv': 'https://tv-v2.api-fetch.website/shows/1',
        'anime': 'https://anime.api-fetch.website/animes/1',
    }

    torrent_state = {}
    transfers = {}

    def __init__(self, download_dir=None, torrent_ports=[], *argv, **kwargs):
        """
        :param download_dir: Directory where the videos/torrents will be downloaded (default: none)
        :type download_dir: str

        :param torrent_ports: Torrent ports to listen on (default: 6881 and 6891)
        :type torrent_ports: list[int]
        """

        super().__init__(*argv, **kwargs)

        self.torrent_ports = torrent_ports if torrent_ports else self.default_torrent_ports
        self.download_dir = None
        self._session = None

        if download_dir:
            self.download_dir = os.path.abspath(os.path.expanduser(download_dir))

    def _search_all(self, query, *args, **kwargs):
        results = {
            category: []
            for category in self.supported_categories.keys()
        }

        def worker(category):
            results[category] = self.search(query, category=category, *args, **kwargs).output

        workers = [
            threading.Thread(target=worker, kwargs={'category': category})
            for category in self.supported_categories.keys()
        ]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        ret = []
        for (category, items) in results.items():
            ret += items
        return ret

    @action
    def search(self, query, category=None, language=None):
        """
        Perform a search of video torrents.

        :param query: Query string, video name or partial name
        :type query: str

        :param category: Category to search. Supported types: "movies", "tv", "anime".
            Default: None (search all categories)
        :type category: str

        :param language: Language code for the results - example: "en" (default: None, no filter)
        :type language: str
        """

        if not category:
            return self._search_all(query, language=language)

        if category not in self.supported_categories:
            raise RuntimeError('Unsupported category {}. Supported category: {}'.
                               format(category, self.supported_categories.keys()))

        self.logger.info('Searching {} torrents for "{}"'.format(category, query))
        request = urllib.request.urlopen(urllib.request.Request(
            self.supported_categories[category] + '?' + urllib.parse.urlencode({
                'sort': 'relevance',
                'keywords': query,
            }),
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' +
                              '(KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
            })
        )

        response = request.read()
        if isinstance(response, bytes):
            response = response.decode('utf-8')

        return sorted([
            {
                'imdb_id': result.get('imdb_id'),
                'type': category,
                'title': '{title} [{category}][{language}][{quality}]'.format(
                    title=result.get('title'), language=lang, quality=quality, category=category),
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
            for result in (json.loads(response) or [])
            for (lang, items) in result.get('torrents', {}).items()
            if not language or language == lang
            for (quality, item) in items.items()
        ], key=lambda _: _.get('seeds'), reverse=True)

    def _get_torrent_info(self, torrent, download_dir):
        import libtorrent as lt

        torrent_file = None
        magnet = None
        info = {}
        file_info = {}

        if torrent.startswith('magnet:?'):
            magnet = torrent
            info = lt.parse_magnet_uri(magnet)
            info['magnet'] = magnet
        elif torrent.startswith('http://') or torrent.startswith('https://'):
            import requests
            response = requests.get(torrent, allow_redirects=True)
            torrent_file = os.path.join(download_dir,
                                        self._generate_rand_filename())

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

        if not self._session:
            self._session = lt.session()

        self._session.listen_on(*self.torrent_ports)

        params = {
            'save_path': download_dir,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        }

        if magnet:
            transfer = lt.add_magnet_uri(self._session, magnet, params)
        else:
            params['ti'] = file_info
            transfer = self._session.add_torrent(params)

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

        if not len(self.transfers):
            self.logger.info('No remaining active torrent transfers found, exiting session')
            self._session = None

    @action
    def quit(self):
        """
        Quits all the transfers and the active session
        """
        if not self._session:
            self.logger.info('No active sessions found')
            return

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
