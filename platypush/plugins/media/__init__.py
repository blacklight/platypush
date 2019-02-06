import enum
import os
import re
import subprocess
import threading

import urllib.request
import urllib.parse

from platypush.config import Config
from platypush.context import get_plugin
from platypush.plugins import Plugin, action
from platypush.utils import get_ip_or_hostname, is_process_alive

class PlayerState(enum.Enum):
    STOP  = 'stop'
    PLAY  = 'play'
    PAUSE = 'pause'


class MediaPlugin(Plugin):
    """
    Generic plugin to interact with a media player.

    Requires:

        * A media player installed (supported so far: mplayer, omxplayer, chromecast)
        * **python-libtorrent** (``pip install python-libtorrent``), optional for Torrent support
        * **youtube-dl** installed on your system (see your distro instructions), optional for YouTube support

    To start the local media stream service over HTTP:

        * **nodejs** installed on your system
        * **express** module (``npm install express``)
        * **mime-types** module (``npm install mime-types``)
    """

    # A media plugin can either be local or remote (e.g. control media on
    # another device)
    _is_local = True

    # Default port for the local resources HTTP streaming service
    _default_streaming_port = 8989

    # setup.py install will place localstream in PATH
    _local_stream_bin = 'localstream'

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
                                'media.chromecast'}

    def __init__(self, media_dirs=[], download_dir=None, env=None,
                 streaming_port=_default_streaming_port, *args, **kwargs):
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

        :param streaming_port: Port to be used for streaming local resources
            over HTTP (default: 8989)
        :type streaming_port: int
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
        self._streaming_port = streaming_port
        self._streaming_proc = None
        self._streaming_started = threading.Event()
        self._streaming_ended = threading.Event()

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
                # The Chromecast has already its way to handle YouTube
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

        results = []
        if types is None:
            types = { 'youtube', 'file', 'torrent' }

        if 'file' in types:
            file_results = self.file_search(query).output
            results.extend(file_results)

        if 'torrent' in types:
            torrents = get_plugin('torrent')
            torrent_results = torrents.search(query).output
            results.extend(torrent_results)

        if 'youtube' in types:
            yt_results = self.youtube_search(query).output
            results.extend(yt_results)

        if results:
            if queue_results:
                self._videos_queue = [_['url'] for _ in results]
                if autoplay:
                    self.play(self._videos_queue.pop(0))
            elif autoplay:
                self.play(results[0]['url'])

        return results

    @classmethod
    def _is_video_file(cls, filename):
        return filename.lower().split('.')[-1] in cls.video_extensions

    @classmethod
    def _is_audio_file(cls, filename):
        return filename.lower().split('.')[-1] in cls.audio_extensions

    @action
    def file_search(self, query):
        results = []
        query_tokens = [_.lower() for _ in re.split('\s+', query.strip())]

        for media_dir in self.media_dirs:
            self.logger.info('Scanning {} for "{}"'.format(media_dir, query))
            for path, dirs, files in os.walk(media_dir):
                for f in files:
                    if not self._is_video_file(f) and not self._is_audio_file(f):
                        continue

                    matches_query = True
                    for token in query_tokens:
                        if token not in f.lower():
                            matches_query = False
                            break

                    if not matches_query:
                        continue

                    results.append({
                        'url': 'file://' + path + os.sep + f,
                        'title': f,
                    })

        return results

    @action
    def youtube_search(self, query):
        """
        Performs a YouTube search either using the YouTube API (faster and
        recommended, it requires the :mod:`platypush.plugins.google.youtube`
        plugin to be configured) or parsing the HTML search results (fallback
        slower method)
        """

        self.logger.info('Searching YouTube for "{}"'.format(query))

        try:
            return self._youtube_search_api(query=query)
        except Exception as e:
            self.logger.warning('Unable to load the YouTube plugin, falling ' +
                                'back to HTML parse method: {}'.format(str(e)))

            return self._youtube_search_html_parse(query=query)


    @action
    def start_streaming(self, media, port=None):
        """
        Starts streaming local media over the specified HTTP port.
        The stream will be available to HTTP clients on
        `http://{this-ip}:{port}/media

        :param media: Media to stream
        """
        if self._streaming_proc:
            self.logger.info('A streaming process is already running, ' +
                             'terminating it first')
            self.stop_streaming()

        if port is None:
            port = self._streaming_port

        self._streaming_started.clear()
        self._streaming_ended.clear()
        self._streaming_proc = subprocess.Popen(
            [self._local_stream_bin, media, str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        threading.Thread(target=self._streaming_process_monitor(media)).start()
        url = 'http://{}:{}/media'.format(get_ip_or_hostname(),
                                          self._streaming_port)

        self.logger.info('Starting streaming {} on {}'.format(media, url))
        self._streaming_started.wait()
        self.logger.info('Started streaming {} on {}'.format(media, url))
        return { 'url': url }

    @action
    def stop_streaming(self):
        if not self._streaming_proc:
            self.logger.info('No streaming process found')
            return

        self._streaming_proc.terminate()
        self._streaming_proc.wait()
        try: self._streaming_proc.kill()
        except: pass
        self._streaming_proc = None


    def _streaming_process_monitor(self, media):
        def _thread():
            if not self._streaming_proc:
                return

            while True:
                if not self._streaming_proc or not \
                        is_process_alive(self._streaming_proc.pid):
                    break

                line = self._streaming_proc.stdout.readline().decode().strip()
                if not line:
                    continue

                if line.startswith('Listening on'):
                    self._streaming_started.set()
                    break

                self.logger.info('Message from streaming service: {}'.format(line))

            self._streaming_proc.wait()
            try: self.stop_streaming()
            except: pass
            self._streaming_ended.set()
            self.logger.info('Streaming service terminated')

        return _thread


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


# vim:sw=4:ts=4:et:
