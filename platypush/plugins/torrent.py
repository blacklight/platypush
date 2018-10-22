import json
import os
import random
import time

import urllib.request
import urllib.parse

from platypush.context import get_bus
from platypush.plugins import Plugin, action
from platypush.message.event.torrent import \
    TorrentDownloadStartEvent, TorrentSeedingStartEvent, \
    TorrentStateChangeEvent, TorrentDownloadProgressEvent, \
    TorrentDownloadCompletedEvent


class TorrentPlugin(Plugin):
    """
    Plugin to control video and media playback on your Raspberry Pi or
    ARM-compatible device using OMXPlayer.

    It can play local files, remote URLs, YouTube URLs and it supports torrents
    search, download and play.

    Requires:

        * **python-libtorrent** (``pip install python-libtorrent``)
        * **requests** (``pip install requests``) [optional] for torrent info URL download
    """

    default_torrent_ports = [6881, 6891]
    torrent_state = {}

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

        if download_dir:
            self.download_dir = os.path.abspath(os.path.expanduser(download_dir))

    @action
    def search(self, query, types=None, queue_results=False, autoplay=False):
        """
        Perform a video search.

        :param query: Query string, video name or partial name
        :type query: str

        :param types: Video types to search (default: ``["youtube", "file", "torrent"]``)
        :type types: list

        :param queue_results: Append the results to the current playing queue (default: False)
        :type queue_results: bool

        :param autoplay: Play the first result of the search (default: False)
        :type autoplay: bool
        """

        self.logger.info('Searching matching torrents for "{}"'.format(query))
        request = urllib.request.urlopen(urllib.request.Request(
            'https://api.apidomain.info/list?' + urllib.parse.urlencode({
                'sort': 'relevance',
                'quality': '720p,1080p,3d',
                'page': 1,
                'keywords': query,
            }),
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' +
                    '(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            })
        )

        response = request.read()
        if isinstance(response, bytes):
            response = response.decode('utf-8')

        return [
            {
                'url': _['items'][0]['torrent_magnet'],
                'title': _['title'],
            }

            for _ in json.loads(response).get('MovieList', [])
        ]

    @action
    def download(self, torrent, download_dir=None):
        """
        Download a torrent.

        :param torrent: Torrent to download. Supported formats:

            * Magnet URLs
            * Torrent URLs
            * Local torrent file

        :type resource: str

        :param download_dir: Directory to download, overrides the default download_dir attribute (default: None)
        :type download_dir: str
        """

        import libtorrent as lt

        if not download_dir:
            if self.download_dir:
                download_dir = self.download_dir
            else:
                raise RuntimeError('download_dir not specified')

        os.makedirs(download_dir, exist_ok=True)
        info = {}
        torrent_file = None
        magnet = None
        bus = get_bus()

        if torrent.startswith('magnet:?'):
            magnet = torrent
            info = lt.parse_magnet_uri(magnet)
        elif torrent.startswith('http://') or torrent.startswith('https://'):
            import requests
            response = requests.get(torrent, allow_redirects=True)
            torrent_file = os.path.join(os.path.expanduser(download_dir),
                                        self._generate_rand_filename())

            with open(torrent_file, 'wb') as f:
                f.write(response.content)
        else:
            torrent_file = os.path.expanduser(torrent)

        if torrent_file:
            file_info = lt.torrent_info(torrent_file)
            info = {
                'name': file_info.name(),
                'url': torrent,
                'trackers': [t.url for t in list(file_info.trackers())],
                'save_path': download_dir,
            }

        ses = lt.session()
        ses.listen_on(*self.torrent_ports)

        self.logger.info('Downloading "{}" to "{}" from [{}]'
                     .format(info['name'], self.download_dir, torrent))

        params = {
            'save_path': download_dir,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        }

        if magnet:
            transfer = lt.add_magnet_uri(ses, magnet, params)
        elif torrent_file:
            params['ti'] = file_info
            transfer = ses.add_torrent(params)

        status = transfer.status()
        files = []

        self.torrent_state = {
            'url': info['url'] or magnet or torrent_file,
            'title': info['name'],
            'trackers': info['trackers'],
            'save_path': info['save_path'],
        }

        bus.post(TorrentDownloadStartEvent(**self.torrent_state))
        last_status = None

        while (not status.is_seeding):
            if not last_status:
                bus.post(TorrentSeedingStartEvent(**self.torrent_state))

            status = transfer.status()
            torrent_file = transfer.torrent_file()
            if torrent_file:
                files = [os.path.join(
                            self.download_dir,
                            torrent_file.files().file_path(i))
                    for i in range(0, torrent_file.files().num_files())
                ]

            self.torrent_state['progress'] = 100 * status.progress
            self.torrent_state['download_rate'] = status.download_rate
            self.torrent_state['upload_rate'] = status.upload_rate
            self.torrent_state['num_peers'] = status.num_peers
            self.torrent_state['state'] = status.state

            if last_status and status.progress != last_status.progress:
                bus.post(TorrentDownloadProgressEvent(**self.torrent_state))

            if not last_status or status.state != last_status.state:
                bus.post(TorrentStateChangeEvent(**self.torrent_state))

            self.logger.info(('Torrent download: {:.2f}% complete (down: {:.1f} kb/s ' +
                         'up: {:.1f} kB/s peers: {} state: {})')
                         .format(status.progress * 100,
                                 status.download_rate / 1000,
                                 status.upload_rate / 1000,
                                 status.num_peers, status.state))

            last_status = status
            time.sleep(5)

        if torrent_file:
            try: os.unlink(torrent_file)
            except: pass

        bus.post(TorrentStateChangeEvent(**self.torrent_state, files=files))
        return files


    @action
    def get_status(self):
        return self.torrent_state

    def _generate_rand_filename(self, length=16):
        name = ''
        for i in range(0, length):
            name += hex(random.randint(0, 15))[2:].upper()
        return name + '.torrent'

# vim:sw=4:ts=4:et:

