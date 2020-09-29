import enum
import functools
import os
import queue
import re
from typing import Optional, List, Dict, Union

import requests
import subprocess
import tempfile
import threading

from platypush.config import Config
from platypush.context import get_plugin, get_backend
from platypush.plugins import Plugin, action


class PlayerState(enum.Enum):
    STOP = 'stop'
    PLAY = 'play'
    PAUSE = 'pause'
    IDLE = 'idle'


class MediaPlugin(Plugin):
    """
    Generic plugin to interact with a media player.

    Requires:

        * A media player installed (supported so far: mplayer, vlc, mpv, omxplayer, chromecast)
        * **python-libtorrent** (``pip install python-libtorrent``), optional, for torrent support over native library
        * *rtorrent* installed - optional, for torrent support over rtorrent
        * **youtube-dl** installed on your system (see your distro instructions), optional for YouTube support
        * **requests** (``pip install requests``), optional, for local files over HTTP streaming supporting
        * **ffmpeg**,optional, to get media files metadata

    To start the local media stream service over HTTP you will also need the
    :class:`platypush.backend.http.HttpBackend` backend enabled.
    """

    # A media plugin can either be local or remote (e.g. control media on
    # another device)
    _is_local = True
    _youtube_fifo = os.path.join(tempfile.gettempdir(), 'youtube_video.sock')
    _NOT_IMPLEMENTED_ERR = NotImplementedError('This method must be implemented in a derived class')

    # Supported audio extensions
    audio_extensions = {
        '3gp', 'aa', 'aac', 'aax', 'act', 'aiff', 'amr', 'ape', 'au',
        'awb', 'dct', 'dss', 'dvf', 'flac', 'gsm', 'iklax', 'ivs',
        'm4a', 'm4b', 'm4p', 'mmf', 'mp3', 'mpc', 'msv', 'nmf', 'nsf',
        'ogg,', 'opus', 'ra,', 'raw', 'sln', 'tta', 'vox', 'wav',
        'wma', 'wv', 'webm', '8svx',
    }

    # Supported video extensions
    video_extensions = {
        'webm', 'mkv', 'flv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gif',
        'gifv', 'mng', 'avi', 'mts', 'm2ts', 'mov', 'qt', 'wmv', 'yuv',
        'rm', 'rmvb', 'asf', 'amv', 'mp4', 'm4p', 'm4v', 'mpg', 'mp2',
        'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg', 'm2v', 'm4v', 'svi',
        '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a',
        'f4b',
    }

    _supported_media_plugins = {'media.mplayer', 'media.omxplayer', 'media.mpv',
                                'media.vlc', 'media.chromecast', 'media.gstreamer'}

    _supported_media_types = ['file', 'torrent', 'youtube']
    _default_search_timeout = 60  # 60 seconds

    def __init__(self,
                 media_dirs: Optional[List[str]] = None,
                 download_dir: Optional[str] = None,
                 env: Optional[Dict[str, str]] = None,
                 volume: Optional[Union[float, int]] = None,
                 torrent_plugin: str = 'torrent',
                 *args, **kwargs):
        """
        :param media_dirs: Directories that will be scanned for media files when
            a search is performed (default: none)

        :param download_dir: Directory where external resources/torrents will be
            downloaded (default: ~/Downloads)

        :param env: Environment variables key-values to pass to the
            player executable (e.g. DISPLAY, XDG_VTNR, PULSE_SINK etc.)

        :param volume: Default volume for the player (default: None, maximum volume).

        :param torrent_plugin: Optional plugin to be used for torrent download. Possible values:

            - ``torrent`` - native ``libtorrent``-based plugin (default)
            - ``rtorrent`` - torrent support over rtorrent RPC/XML interface (recommended)
            - ``webtorrent`` - torrent support over webtorrent (unstable)

        """

        super().__init__(**kwargs)

        if media_dirs is None:
            media_dirs = []
        player = None
        player_config = {}

        if self.__class__.__name__ == 'MediaPlugin':
            # Abstract class, initialize with the default configured player
            for plugin in Config.get_plugins().keys():
                if plugin in self._supported_media_plugins:
                    player = plugin
                    if get_plugin(player).is_local():
                        # Local players have priority as default if configured
                        break
        else:
            player = self  # Derived concrete class

        if not player:
            raise AttributeError('No media plugin configured')

        media_dirs = media_dirs or player_config.get('media_dirs', [])

        if self.__class__.__name__ == 'MediaPlugin':
            # Populate this plugin with the actions of the configured player
            plugin = get_plugin(player)
            for act in plugin.registered_actions:
                setattr(self, act, getattr(plugin, act))
                self.registered_actions.add(act)

        self._env = env or {}
        self.media_dirs = set(
            filter(
                lambda _: os.path.isdir(_),
                map(
                    lambda _: os.path.abspath(os.path.expanduser(_)),
                    media_dirs
                )
            )
        )

        self.download_dir = os.path.abspath(os.path.expanduser(
            download_dir or player_config.get('download_dir') or
            os.path.join((os.path.expanduser('~') or self._env.get('HOME') or '/'), 'Downloads')))

        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)

        self.media_dirs.add(self.download_dir)
        self.volume = volume
        self._videos_queue = []
        self._youtube_proc = None
        self.torrent_plugin = torrent_plugin

    @staticmethod
    def _torrent_event_handler(evt_queue):
        def handler(event):
            # More than 5% of the torrent has been downloaded
            if event.args.get('progress', 0) > 5 and event.args.get('files'):
                evt_queue.put(event.args['files'])
        return handler

    def _get_resource(self, resource):
        """
        :param resource: Resource to play/parse. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * YouTube videos (format: ``https://www.youtube.com/watch?v=<id>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)
        """

        if resource.startswith('youtube:') \
                or resource.startswith('https://youtu.be/') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            m = re.match('youtube:video:(.*)', resource)
            if not m:
                m = re.match('https://youtu.be/(.*)', resource)
            if m:
                resource = 'https://www.youtube.com/watch?v={}'.format(m.group(1))

            if self.__class__.__name__ == 'MediaChromecastPlugin':
                # The Chromecast has already its native way to handle YouTube
                return resource

            self.stream_youtube_to_fifo(resource)
            resource = 'file://' + self._youtube_fifo
        elif resource.startswith('magnet:?'):
            self.logger.info('Downloading torrent {} to {}'.format(
                resource, self.download_dir))
            torrents = get_plugin(self.torrent_plugin)

            evt_queue = queue.Queue()
            torrents.download(resource, download_dir=self.download_dir, _async=True, is_media=True,
                              event_hndl=self._torrent_event_handler(evt_queue))

            resources = [f for f in evt_queue.get()]

            if resources:
                self._videos_queue = sorted(resources)
                resource = self._videos_queue.pop(0)
            else:
                raise RuntimeError('No media file found in torrent {}'.format(resource))

        return resource

    def _stop_torrent(self):
        torrents = get_plugin(self.torrent_plugin)
        torrents.quit()

    @action
    def play(self, resource, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def pause(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def stop(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def quit(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def voldown(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def volup(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def back(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def forward(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def next(self):
        """ Play the next item in the queue """
        self.stop()

        if self._videos_queue:
            video = self._videos_queue.pop(0)
            return self.play(video)

    @action
    def toggle_subtitles(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def set_subtitles(self, filename, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def remove_subtitles(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def is_playing(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def load(self, resource, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def mute(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def seek(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def set_position(self, *args, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def set_volume(self, volume):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def status(self):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def search(self, query, types=None, queue_results=False, autoplay=False,
               search_timeout=_default_search_timeout):
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

        :param search_timeout: Search timeout (default: 60 seconds)
        :type search_timeout: float
        """

        results = {}
        results_queues = {}
        worker_threads = {}

        if types is None:
            types = self._supported_media_types

        for media_type in types:
            results[media_type] = []
            results_queues[media_type] = queue.Queue()
            search_hndl = self._get_search_handler_by_type(media_type)
            worker_threads[media_type] = threading.Thread(
                target=self._search_worker(query=query, search_hndl=search_hndl,
                                           results_queue=results_queues[media_type]))
            worker_threads[media_type].start()

        for media_type in types:
            try:
                results[media_type].extend(
                    results_queues[media_type].get(timeout=search_timeout))
            except queue.Empty:
                self.logger.warning('Search for "{}" media type {} timed out'.
                                    format(query, media_type))

        flattened_results = []

        for media_type in self._supported_media_types:
            if media_type in results:
                for result in results[media_type]:
                    result['type'] = media_type
                flattened_results += results[media_type]

        results = flattened_results

        if results:
            if queue_results:
                self._videos_queue = [_['url'] for _ in results]
                if autoplay:
                    self.play(self._videos_queue.pop(0))
            elif autoplay:
                self.play(results[0]['url'])

        return results

    @staticmethod
    def _search_worker(query, search_hndl, results_queue):
        def thread():
            results_queue.put(search_hndl.search(query))
        return thread

    def _get_search_handler_by_type(self, search_type):
        if search_type == 'file':
            from .search import LocalMediaSearcher
            return LocalMediaSearcher(self.media_dirs)
        if search_type == 'torrent':
            from .search import TorrentMediaSearcher
            return TorrentMediaSearcher()
        if search_type == 'youtube':
            from .search import YoutubeMediaSearcher
            return YoutubeMediaSearcher()

        self.logger.warning('Unsupported search type: {}'.format(search_type))

    @classmethod
    def _is_video_file(cls, filename):
        return filename.lower().split('.')[-1] in cls.video_extensions

    @classmethod
    def _is_audio_file(cls, filename):
        return filename.lower().split('.')[-1] in cls.audio_extensions

    @action
    def start_streaming(self, media, subtitles=None, download=False):
        """
        Starts streaming local media over the specified HTTP port.
        The stream will be available to HTTP clients on
        `http://{this-ip}:{http_backend_port}/media/<media_id>`

        :param media: Media to stream
        :type media: str

        :param subtitles: Path or URL to the subtitles track to be used
        :type subtitles: str

        :param download: Set to True if you prefer to download the file from
            the streaming link instead of streaming it
        :type download: bool

        :return: dict containing the streaming URL.Example:

        .. code-block:: json

            {
                "id": "0123456abcdef.mp4",
                "source": "file:///mnt/media/movies/movie.mp4",
                "mime_type": "video/mp4",
                "url": "http://192.168.1.2:8008/media/0123456abcdef.mp4"
            }

        """
        import requests

        http = get_backend('http')
        if not http:
            self.logger.warning('Unable to stream {}: HTTP backend unavailable'.
                                format(media))
            return

        self.logger.info('Starting streaming {}'.format(media))
        response = requests.put('{url}/media{download}'.format(
            url=http.local_base_url, download='?download' if download else ''),
            json={'source': media, 'subtitles': subtitles})

        if not response.ok:
            self.logger.warning('Unable to start streaming: {}'.
                                format(response.text or response.reason))
            return None, (response.text or response.reason)

        return response.json()

    @action
    def stop_streaming(self, media_id):
        import requests

        http = get_backend('http')
        if not http:
            self.logger.warning('Cannot unregister {}: HTTP backend unavailable'.
                                format(media_id))
            return

        response = requests.delete('{url}/media/{id}'.
                                   format(url=http.local_base_url, id=media_id))

        if not response.ok:
            self.logger.warning('Unable to unregister media_id {}: {}'.format(
                media_id, response.reason))
            return

        return response.json()

    @staticmethod
    def _youtube_search_api(query):
        return [
            {
                'url': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                'title': item.get('snippet', {}).get('title', '<No Title>'),
            }
            for item in get_plugin('google.youtube').search(query=query).output
            if item.get('id', {}).get('kind') == 'youtube#video'
        ]

    @staticmethod
    def _youtube_search_html_parse(query):
        from .search import YoutubeMediaSearcher
        # noinspection PyProtectedMember
        return YoutubeMediaSearcher()._youtube_search_html_parse(query)

    def stream_youtube_to_fifo(self, url):
        if self._youtube_proc:
            self.logger.info('Terminating existing YouTube process')
            self._youtube_proc.terminate()
            self._youtube_proc = None

        if os.path.exists(self._youtube_fifo):
            os.unlink(self._youtube_fifo)

        os.mkfifo(self._youtube_fifo, 0o644)

        def _youtube_dl_thread():
            self._youtube_proc = subprocess.Popen(['youtube-dl', '-f', 'best', '-o', self._youtube_fifo, url])
            self._youtube_proc.wait()
            self._youtube_proc = None

        threading.Thread(target=_youtube_dl_thread).start()

    @staticmethod
    def get_youtube_id(url: str) -> Optional[str]:
        patterns = [
            re.compile(pattern)
            for pattern in [
                r'https?://www.youtube.com/watch\?v=([^&#]+)',
                r'https?://youtube.com/watch\?v=([^&#]+)',
                r'https?://youtu.be/([^&#/]+)',
                r'youtube:video:([^&#:])',
            ]
        ]

        for pattern in patterns:
            m = pattern.search(url)
            if m:
                return m.group(1)

    @action
    def get_youtube_url(self, url):
        youtube_id = self.get_youtube_id(url)
        if youtube_id:
            url = 'https://www.youtube.com/watch?v={}'.format(youtube_id)
            proc = subprocess.Popen(['youtube-dl', '-f', 'best', '-g', url], stdout=subprocess.PIPE)
            raw_url = proc.stdout.read().decode("utf-8", "strict")[:-1]
            return raw_url if raw_url else url

    @action
    def get_youtube_info(self, url):
        m = re.match('youtube:video:(.*)', url)
        if m:
            url = 'https://www.youtube.com/watch?v={}'.format(m.group(1))

        proc = subprocess.Popen(['youtube-dl', '-j', url], stdout=subprocess.PIPE)
        return proc.stdout.read().decode("utf-8", "strict")[:-1]

    @action
    def get_media_file_duration(self, filename):
        """
        Get the duration of a media file in seconds. Requires ffmpeg
        """

        if filename.startswith('file://'):
            filename = filename[7:]

        result = subprocess.Popen(["ffprobe", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return functools.reduce(
            lambda t, t_i: t + t_i,
            [float(t) * pow(60, i) for (i, t) in enumerate(re.search(
                '^Duration:\s*([^,]+)', [x.decode()
                                         for x in result.stdout.readlines()
                                         if "Duration" in x.decode()].pop().strip()
            ).group(1).split(':')[::-1])]
        )

    @action
    def download(self, url, filename=None, directory=None):
        """
        Download a media URL

        :param url: Media URL
        :param filename: Media filename (default: URL filename)
        :param directory: Destination directory (default: download_dir)
        :return: The absolute path to the downloaded file
        """

        if not filename:
            filename = url.split('/')[-1]
        if not directory:
            directory = self.download_dir

        path = os.path.join(directory, filename)
        content = requests.get(url).content

        with open(path, 'wb') as f:
            f.write(content)

        return path

    def is_local(self):
        return self._is_local

    @staticmethod
    def get_subtitles_file(subtitles):
        if not subtitles:
            return

        if subtitles.startswith('file://'):
            subtitles = subtitles[len('file://'):]
        if os.path.isfile(subtitles):
            return os.path.abspath(subtitles)
        else:
            content = requests.get(subtitles).content
            f = tempfile.NamedTemporaryFile(prefix='media_subs_',
                                            suffix='.srt', delete=False)

            with f:
                f.write(content)
            return f.name


# vim:sw=4:ts=4:et:
