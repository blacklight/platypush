import enum
import os
import queue
import re
import subprocess
import threading

import urllib.request
import urllib.parse

from platypush.config import Config
from platypush.context import get_plugin, get_backend
from platypush.plugins import Plugin, action


class PlayerState(enum.Enum):
    STOP  = 'stop'
    PLAY  = 'play'
    PAUSE = 'pause'


class MediaPlugin(Plugin):
    """
    Generic plugin to interact with a media player.

    Requires:

        * A media player installed (supported so far: mplayer, mpv, omxplayer, chromecast)
        * The :class:`platypush.plugins.media.webtorrent` plugin for optional torrent support through webtorrent (recommented)
        * **python-libtorrent** (``pip install python-libtorrent``), optional, for torrent support through the native Python plugin
        * **youtube-dl** installed on your system (see your distro instructions), optional for YouTube support
        * **requests** (``pip install requests``), optional, for local files over HTTP streaming supporting

    To start the local media stream service over HTTP you will also need the
    :class:`platypush.backend.http.HttpBackend` backend enabled.
    """

    # A media plugin can either be local or remote (e.g. control media on
    # another device)
    _is_local = True

    _NOT_IMPLEMENTED_ERR = NotImplementedError(
        'This method must be implemented in a derived class')

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

    _supported_media_plugins = {'media.mplayer', 'media.omxplayer',
                                'media.mpv', 'media.chromecast'}

    _supported_media_types = ['file', 'torrent', 'youtube']
    _default_search_timeout = 60  # 60 seconds

    def __init__(self, media_dirs=[], download_dir=None, env=None,
                 *args, **kwargs):
        """
        :param media_dirs: Directories that will be scanned for media files when
            a search is performed (default: none)
        :type media_dirs: list

        :param download_dir: Directory where external resources/torrents will be
            downloaded (default: none)
        :type download_dir: str

        :param env: Environment variables key-values to pass to the
            player executable (e.g. DISPLAY, XDG_VTNR, PULSE_SINK etc.)
        :type env: dict
        """

        super().__init__(*args, **kwargs)

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
        download_dir = download_dir or player_config.get('download_dir')

        if self.__class__.__name__ == 'MediaPlugin':
            # Populate this plugin with the actions of the configured player
            plugin = get_plugin(player)
            for action in plugin.registered_actions:
                setattr(self, action, getattr(plugin, action))
                self.registered_actions.add(action)

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

        if download_dir:
            self.download_dir = os.path.abspath(os.path.expanduser(download_dir))
            if not os.path.isdir(self.download_dir):
                raise RuntimeError('download_dir [{}] is not a valid directory'
                                   .format(self.download_dir))

            self.media_dirs.add(self.download_dir)

        self._videos_queue = []

    def _get_resource(self, resource):
        """
        :param resource: Resource to play/parse. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * YouTube videos (format: ``https://www.youtube.com/watch?v=<id>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)
        """

        if resource.startswith('youtube:') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            if self.__class__.__name__ == 'MediaChromecastPlugin':
                # The Chromecast has already its native way to handle YouTube
                return resource

            resource = self._get_youtube_content(resource)
        elif resource.startswith('magnet:?'):
            try:
                get_plugin('media.webtorrent')
                return resource  # media.webtorrent will handle this
            except:
                pass

            torrents = get_plugin('torrent')
            self.logger.info('Downloading torrent {} to {}'.format(
                resource, self.download_dir))

            response = torrents.download(resource, download_dir=self.download_dir)
            resources = [f for f in response.output if self._is_video_file(f)]
            if resources:
                self._videos_queue = sorted(resources)
                resource = self._videos_queue.pop(0)
            else:
                raise RuntimeError('Unable to download torrent {}'.format(resource))

        return resource

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
        if self.player:
            self.player.stop()

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
    def set_volume(self, volume, *args, **kwargs):
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

    def _search_worker(self, query, search_hndl, results_queue):
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
    def start_streaming(self, media, download=False):
        """
        Starts streaming local media over the specified HTTP port.
        The stream will be available to HTTP clients on
        `http://{this-ip}:{http_backend_port}/media/<media_id>`

        :param media: Media to stream
        :type media: str

        :param download: Set to True if you prefer to download the file from
            the streaming link instead of streaming it
        :type download: bool

        :returns: dict containing the streaming URL.Example::

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
            json = { 'source': media })

        if not response.ok:
            self.logger.warning('Unable to start streaming: {}'.
                                format(response.text or response.reason))
            return

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


    def _youtube_search_api(self, query):
        return [
            {
                'url': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                'title': item.get('snippet', {}).get('title', '<No Title>'),
            }
            for item in get_plugin('google.youtube').search(query=query).output
            if item.get('id', {}).get('kind') == 'youtube#video'
        ]

    def _youtube_search_html_parse(self, query):
        query = urllib.parse.quote(query)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
        results = []

        while html:
            m = re.search('(<a href="(/watch\?v=.+?)".+?yt-uix-tile-link.+?title="(.+?)".+?>)', html)
            if m:
                results.append({
                    'url': 'https://www.youtube.com' + m.group(2),
                    'title': m.group(3)
                })

                html = html.split(m.group(1))[1]
            else:
                html = ''

        self.logger.info('{} YouTube video results for the search query "{}"'
                     .format(len(results), query))

        return results


    @classmethod
    def _get_youtube_content(cls, url):
        m = re.match('youtube:video:(.*)', url)
        if m: url = 'https://www.youtube.com/watch?v={}'.format(m.group(1))

        proc = subprocess.Popen(['youtube-dl','-f','best', '-g', url],
                                stdout=subprocess.PIPE)

        return proc.stdout.read().decode("utf-8", "strict")[:-1]


    def is_local(self):
        return self._is_local


    def get_subtitles_file(self, subtitles):
        if not subtitles:
            return

        if subtitles.startswith('file://'):
            subtitles = subtitles[len('file://'):]
        if os.path.isfile(subtitles):
            return os.path.abspath(subtitles)
        else:
            import requests
            content = requests.get(subtitles).content
            f = tempfile.NamedTemporaryFile(prefix='media_subs_',
                                            suffix='.srt', delete=False)

            with f:
                f.write(content)
            return f.name


# vim:sw=4:ts=4:et:
