import functools
import inspect
import json
import os
import queue
import re
import subprocess
import tempfile
import threading
from abc import ABC, abstractmethod
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

import requests

from platypush.config import Config
from platypush.context import get_plugin, get_backend
from platypush.message.event.media import MediaEvent
from platypush.plugins import RunnablePlugin, action
from platypush.utils import get_default_downloads_dir, get_plugin_name_by_class

from ._download import (
    DownloadState,
    DownloadThread,
    FileDownloadThread,
    YouTubeDownloadThread,
)
from ._resource import MediaResource
from ._state import PlayerState


class MediaPlugin(RunnablePlugin, ABC):
    """
    Generic plugin to interact with a media player.

    To start the local media stream service over HTTP you will also need the
    :class:`platypush.backend.http.HttpBackend` backend enabled.
    """

    # A media plugin can either be local or remote (e.g. control media on
    # another device)
    _is_local = True
    _NOT_IMPLEMENTED_ERR = NotImplementedError(
        'This method must be implemented in a derived class'
    )

    # Supported audio extensions
    audio_extensions = {
        '3gp',
        'aa',
        'aac',
        'aax',
        'act',
        'aiff',
        'amr',
        'ape',
        'au',
        'awb',
        'dct',
        'dss',
        'dvf',
        'flac',
        'gsm',
        'iklax',
        'ivs',
        'm4a',
        'm4b',
        'm4p',
        'mmf',
        'mp3',
        'mpc',
        'msv',
        'nmf',
        'nsf',
        'ogg,',
        'opus',
        'ra,',
        'raw',
        'sln',
        'tta',
        'vox',
        'wav',
        'wma',
        'wv',
        'webm',
        '8svx',
    }

    # Supported video extensions
    video_extensions = {
        'webm',
        'mkv',
        'flv',
        'vob',
        'ogv',
        'ogg',
        'drc',
        'gif',
        'gifv',
        'mng',
        'avi',
        'mts',
        'm2ts',
        'mov',
        'qt',
        'wmv',
        'yuv',
        'rm',
        'rmvb',
        'asf',
        'amv',
        'mp4',
        'm4p',
        'm4v',
        'mpg',
        'mp2',
        'mpeg',
        'mpe',
        'mpv',
        'm2v',
        'svi',
        '3gp',
        '3g2',
        'mxf',
        'roq',
        'nsv',
        'f4v',
        'f4p',
        'f4a',
        'f4b',
    }

    supported_media_plugins = [
        'media.mplayer',
        'media.omxplayer',
        'media.mpv',
        'media.vlc',
        'media.chromecast',
        'media.gstreamer',
    ]

    _supported_media_types = ['file', 'jellyfin', 'plex', 'torrent', 'youtube']
    _default_search_timeout = 60  # 60 seconds

    def __init__(
        self,
        media_dirs: Optional[List[str]] = None,
        download_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        volume: Optional[Union[float, int]] = None,
        torrent_plugin: str = 'torrent',
        youtube_format: Optional[str] = 'bv[height<=?1080][ext=mp4]+ba',
        youtube_dl: str = 'yt-dlp',
        **kwargs,
    ):
        """
        :param media_dirs: Directories that will be scanned for media files when
            a search is performed (default: none)

        :param download_dir: Directory where external resources/torrents will be
            downloaded (default: ~/Downloads)

        :param env: Environment variables key-values to pass to the
            player executable (e.g. DISPLAY, XDG_VTNR, PULSE_SINK etc.)

        :param volume: Default volume for the player (default: None, maximum volume).

        :param torrent_plugin: Optional plugin to be used for torrent download. Possible values:

            - ``torrent`` - native ``libtorrent``-based plugin (default, recommended)
            - ``rtorrent`` - torrent support over rtorrent RPC/XML interface
            - ``webtorrent`` - torrent support over webtorrent (unstable)

        :param youtube_format: Select the preferred video/audio format for
            YouTube videos - and any media supported by youtube-dl or the
            selected fork. See the `youtube-dl documentation
            <https://github.com/ytdl-org/youtube-dl#format-selection>`_ for more
            info on supported formats. Default:
            ``bv*[height<=?1080][ext=mp4]+bestaudio/best`` - select the best
            mp4 video with a resolution <= 1080p, and the best audio format.

        :param youtube_dl: Path to the ``youtube-dl`` executable, used to
            extract information from YouTube videos and other media platforms.
            Default: ``yt-dlp``. The default has changed from ``youtube-dl`` to
            the ``yt-dlp`` fork because the former is badly maintained and its
            latest release was pushed in 2021.
        """

        super().__init__(**kwargs)

        if media_dirs is None:
            media_dirs = []
        player = None
        player_config = {}
        self._download_threads: Dict[Tuple[str, str], DownloadThread] = {}

        if self.__class__.__name__ == 'MediaPlugin':
            # Abstract class, initialize with the default configured player
            for plugin_name in Config.get_plugins().keys():
                if plugin_name in self.supported_media_plugins:
                    player = get_plugin(plugin_name)
                    if player and player.is_local():
                        # Local players have priority as default if configured
                        break
        else:
            player = self  # Derived concrete class

        if not player:
            raise AttributeError('No media plugin configured')

        media_dirs = media_dirs or player_config.get('media_dirs', [])

        if self.__class__.__name__ == 'MediaPlugin':
            # Populate this plugin with the actions of the configured player
            for act in player.registered_actions:
                setattr(self, act, getattr(player, act))
                self.registered_actions.add(act)

        self._env = env or {}
        self.media_dirs = set(
            filter(
                os.path.isdir,
                [os.path.abspath(os.path.expanduser(d)) for d in media_dirs],
            )
        )

        self.download_dir = os.path.abspath(
            os.path.expanduser(
                download_dir
                or player_config.get('download_dir')
                or get_default_downloads_dir()
            )
        )

        os.makedirs(self.download_dir, exist_ok=True)
        self._ytdl = youtube_dl
        self.media_dirs.add(self.download_dir)
        self.volume = volume
        self._videos_queue = []
        self._youtube_proc = None
        self.torrent_plugin = torrent_plugin
        self.youtube_format = youtube_format
        self._latest_resource: Optional[MediaResource] = None

    @staticmethod
    def _torrent_event_handler(evt_queue):
        def handler(event):
            # More than 5% of the torrent has been downloaded
            if event.args.get('progress', 0) > 5 and event.args.get('files'):
                evt_queue.put(event.args['files'])

        return handler

    def get_extractors(self):
        try:
            from yt_dlp.extractor import _extractors  # type: ignore
        except ImportError:
            self.logger.debug('yt_dlp not installed')
            return

        for _, obj_type in inspect.getmembers(_extractors):
            if (
                inspect.isclass(obj_type)
                and isinstance(getattr(obj_type, "_VALID_URL", None), str)
                and obj_type.__name__ != "GenericIE"
            ):
                yield obj_type

    def _is_youtube_resource(self, resource: str):
        return any(
            re.search(getattr(extractor, '_VALID_URL', '^$'), resource)
            for extractor in self.get_extractors()
        )

    def _get_youtube_best_thumbnail(self, info: Dict[str, dict]):
        thumbnails = info.get('thumbnails', {})
        if not thumbnails:
            return None

        # Preferred resolution
        for res in ((640, 480), (480, 360), (320, 240)):
            thumb = next(
                (
                    thumb
                    for thumb in thumbnails
                    if thumb.get('width') == res[0] and thumb.get('height') == res[1]
                ),
                None,
            )

            if thumb:
                return thumb.get('url')

        # Default fallback (best quality)
        return info.get('thumbnail')

    def _get_resource(self, resource: str):
        """
        :param resource: Resource to play/parse. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)
            * Any URL that is supported by a yt_dlp extractor

        """

        if resource.startswith('file://'):
            path = resource[len('file://') :]
            assert os.path.isfile(path), f'File {path} not found'
            self._latest_resource = MediaResource(
                resource=resource,
                url=resource,
                title=os.path.basename(resource),
                filename=os.path.basename(resource),
            )
        elif self._is_youtube_resource(resource):
            info = self._get_youtube_info(resource)
            if info:
                url = info.get('url')
                if url:
                    resource = url
                    self._latest_resource = MediaResource(
                        resource=resource,
                        url=resource,
                        title=info.get('title'),
                        description=info.get('description'),
                        filename=info.get('filename'),
                        image=info.get('thumbnail'),
                        duration=float(info.get('duration') or 0) or None,
                        channel=info.get('channel'),
                        channel_url=info.get('channel_url'),
                        resolution=info.get('resolution'),
                        type=info.get('extractor'),
                    )
        elif resource.startswith('magnet:?'):
            self.logger.info(
                'Downloading torrent %s to %s', resource, self.download_dir
            )
            torrents = get_plugin(self.torrent_plugin)
            assert torrents, f'{self.torrent_plugin} plugin not configured'

            evt_queue = queue.Queue()
            torrents.download(
                resource,
                download_dir=self.download_dir,
                _async=True,
                is_media=True,
                event_hndl=self._torrent_event_handler(evt_queue),
            )

            resources = [f for f in evt_queue.get()]  # noqa: C416,R1721

            if resources:
                self._videos_queue = sorted(resources)
                resource = self._videos_queue.pop(0)
            else:
                raise RuntimeError(f'No media file found in torrent {resource}')

        assert resource, 'Unable to find any compatible media resource'
        return resource

    def _stop_torrent(self):
        try:
            torrents = get_plugin(self.torrent_plugin)
            assert torrents, f'{self.torrent_plugin} plugin not configured'
            torrents.quit()
        except Exception as e:
            self.logger.warning('Could not stop torrent plugin: %s', e)

    @action
    @abstractmethod
    def play(self, resource, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def pause(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def stop(self, *args, **kwargs):  # type: ignore
        super().stop()

    @action
    @abstractmethod
    def quit(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def voldown(self, step: Optional[float] = 5.0, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def volup(self, step: Optional[float] = 5.0, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def back(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def forward(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def next(self):
        """Play the next item in the queue"""
        self.stop()

        if self._videos_queue:
            video = self._videos_queue.pop(0)
            return self.play(video)

        return None

    @action
    @abstractmethod
    def toggle_subtitles(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def set_subtitles(self, filename, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def remove_subtitles(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def is_playing(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def load(self, resource, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def mute(self, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def seek(self, position, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def set_position(self, position, **kwargs):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def set_volume(self, volume):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    @abstractmethod
    def status(self):
        raise self._NOT_IMPLEMENTED_ERR

    @action
    def search(
        self,
        query: str,
        types: Optional[Iterable[str]] = None,
        queue_results: bool = False,
        autoplay: bool = False,
        timeout: float = _default_search_timeout,
    ):
        """
        Perform a video search.

        :param query: Query string, video name or partial name
        :param types: Video types to search (default: ``["youtube", "file", "torrent"]``)
        :param queue_results: Append the results to the current playing queue (default: False)
        :param autoplay: Play the first result of the search (default: False)
        :param timeout: Search timeout (default: 60 seconds)
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
                target=self._search_worker(
                    query=query,
                    search_hndl=search_hndl,
                    results_queue=results_queues[media_type],
                )
            )
            worker_threads[media_type].start()

        for media_type in types:
            try:
                items = results_queues[media_type].get(timeout=timeout)
                if isinstance(items, Exception):
                    raise items

                results[media_type].extend(items)
            except queue.Empty:
                self.logger.warning(
                    'Search for "%s" media type %s timed out', query, media_type
                )
            except Exception as e:
                self.logger.warning(
                    'Error while searching for "%s", media type %s', query, media_type
                )
                self.logger.exception(e)

        results = [
            {**result, 'type': media_type}
            for media_type in self._supported_media_types
            for result in results.get(media_type, [])
            if media_type in results
        ]

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
            try:
                results_queue.put(search_hndl.search(query))
            except Exception as e:
                results_queue.put(e)

        return thread

    def _get_search_handler_by_type(self, search_type: str):
        if search_type == 'file':
            from .search import LocalMediaSearcher

            return LocalMediaSearcher(self.media_dirs, media_plugin=self)
        if search_type == 'torrent':
            from .search import TorrentMediaSearcher

            return TorrentMediaSearcher(media_plugin=self)
        if search_type == 'youtube':
            from .search import YoutubeMediaSearcher

            return YoutubeMediaSearcher(media_plugin=self)
        if search_type == 'plex':
            from .search import PlexMediaSearcher

            return PlexMediaSearcher(media_plugin=self)
        if search_type == 'jellyfin':
            from .search import JellyfinMediaSearcher

            return JellyfinMediaSearcher(media_plugin=self)

        self.logger.warning('Unsupported search type: %s', search_type)
        return None

    @classmethod
    def is_video_file(cls, filename: str):
        return filename.lower().split('.')[-1] in cls.video_extensions

    @classmethod
    def is_audio_file(cls, filename: str):
        return filename.lower().split('.')[-1] in cls.audio_extensions

    def _get_info(self, resource: str):
        if self._is_youtube_resource(resource):
            return self.get_youtube_info(resource)

        return {'url': resource}

    @action
    def start_streaming(
        self, media: str, subtitles: Optional[str] = None, download: bool = False
    ):
        """
        Starts streaming local media over the specified HTTP port.
        The stream will be available to HTTP clients on
        `http://{this-ip}:{http_backend_port}/media/<media_id>`

        :param media: Media to stream
        :param subtitles: Path or URL to the subtitles track to be used
        :param download: Set to True if you prefer to download the file from
            the streaming link instead of streaming it
        :return: dict containing the streaming URL.Example:

        .. code-block:: json

            {
                "id": "0123456abcdef.mp4",
                "source": "file:///mnt/media/movies/movie.mp4",
                "mime_type": "video/mp4",
                "url": "http://192.168.1.2:8008/media/0123456abcdef.mp4"
            }

        """
        return self._start_streaming(media, subtitles=subtitles, download=download)

    def _start_streaming(
        self, media: str, subtitles: Optional[str] = None, download: bool = False
    ):
        http = get_backend('http')
        assert http, f'Unable to stream {media}: HTTP backend not configured'

        self.logger.info('Starting streaming %s', media)
        response = requests.put(
            f'{http.local_base_url}/media' + ('?download' if download else ''),
            json={'source': media, 'subtitles': subtitles},
            timeout=300,
        )

        assert response.ok, response.text or response.reason
        return response.json()

    @action
    def stop_streaming(self, media_id: str):
        http = get_backend('http')
        assert http, f'Unable to stop streaming {media_id}: HTTP backend not configured'

        response = requests.delete(
            f'{http.local_base_url}/media/{media_id}', timeout=30
        )

        assert response.ok, response.text or response.reason
        return response.json()

    def _get_youtube_info(self, url, youtube_format: Optional[str] = None):
        ytdl_cmd = [
            self._ytdl,
            *(
                ['-f', youtube_format or self.youtube_format]
                if youtube_format or self.youtube_format
                else []
            ),
            '-j',
            '-g',
            url,
        ]

        self.logger.info('Executing command %s', ' '.join(ytdl_cmd))
        with subprocess.Popen(ytdl_cmd, stdout=subprocess.PIPE) as ytdl:
            output = ytdl.communicate()[0].decode().strip()
            ytdl.wait()

        self.logger.debug('yt-dlp output: %s', output)
        lines = output.split('\n')

        if not lines:
            self.logger.warning('No output from yt-dlp')
            return None

        stream_url = lines[1] if len(lines) > 2 else lines[0]
        info = lines[-1]
        return {
            **json.loads(info),
            'url': stream_url,
        }

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

        return None

    @action
    def get_youtube_info(self, url):
        # Legacy conversion for Mopidy YouTube URIs
        m = re.match('youtube:video:(.*)', url)
        if m:
            url = f'https://www.youtube.com/watch?v={m.group(1)}'

        with subprocess.Popen([self._ytdl, '-j', url], stdout=subprocess.PIPE) as proc:
            if proc.stdout is None:
                return None

            return proc.stdout.read().decode("utf-8", "strict")[:-1]

    @action
    def get_info(self, resource: str):
        return self._get_info(resource)

    @action
    def get_media_file_duration(self, filename):
        """
        Get the duration of a media file in seconds. Requires ffmpeg
        """

        if filename.startswith('file://'):
            filename = filename[7:]

        with subprocess.Popen(
            ["ffprobe", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ) as result:
            if not result.stdout:
                return 0

            return functools.reduce(
                lambda t, t_i: t + t_i,
                [
                    float(t) * pow(60, i)
                    for (i, t) in enumerate(
                        re.search(
                            r'^Duration:\s*([^,]+)',
                            [
                                x.decode()
                                for x in result.stdout.readlines()
                                if "Duration" in x.decode()
                            ]
                            .pop()
                            .strip(),
                        )
                        .group(1)  # type: ignore
                        .split(':')[::-1]
                    )
                ],
            )

    @action
    def download(
        self,
        url: str,
        filename: Optional[str] = None,
        directory: Optional[str] = None,
        timeout: int = 10,
        sync: bool = False,
        only_audio: bool = False,
        youtube_format: Optional[str] = None,
    ):
        """
        Download a media URL to a local file on the Platypush host (yt-dlp
        required for YouTube URLs).

        This action is non-blocking and returns the path to the downloaded file
        once the download is initiated.

        You can then subscribe to these events to monitor the download progress:

            - :class:`platypush.message.event.media.MediaDownloadStartedEvent`
            - :class:`platypush.message.event.media.MediaDownloadProgressEvent`
            - :class:`platypush.message.event.media.MediaDownloadErrorEvent`
            - :class:`platypush.message.event.media.MediaDownloadPausedEvent`
            - :class:`platypush.message.event.media.MediaDownloadResumedEvent`
            - :class:`platypush.message.event.media.MediaDownloadCancelledEvent`
            - :class:`platypush.message.event.media.MediaDownloadCompletedEvent`

        :param url: Media URL.
        :param filename: Media filename (default: inferred from the URL basename).
        :param directory: Destination directory (default: ``download_dir``).
        :param timeout: Network timeout in seconds (default: 10).
        :param sync: If set to True, the download will be synchronous and the
            action will return only when the download is completed.
        :param only_audio: If set to True, only the audio track will be downloaded
            (only supported for yt-dlp-compatible URLs for now).
        :param youtube_format: Override the default ``youtube_format`` setting.
        :return: The absolute path to the downloaded file.
        """
        path = self._get_download_path(
            url, directory=directory, filename=filename, youtube_format=youtube_format
        )

        if self._is_youtube_resource(url):
            dl_thread = self._download_youtube_url(
                url, path, youtube_format=youtube_format, only_audio=only_audio
            )
        else:
            if only_audio:
                self.logger.warning(
                    'Only audio download is not supported for non-YouTube URLs'
                )

            dl_thread = self._download_url(url, path, timeout=timeout)

        if sync:
            dl_thread.join()

        return path

    @action
    def pause_download(self, url: Optional[str] = None, path: Optional[str] = None):
        """
        Pause a download in progress.

        Either the URL or the path must be specified.

        :param url: URL of the download.
        :param path: Path of the download (default: any path associated with the URL).
        """
        for thread in self._get_downloads(url=url, path=path):
            thread.pause()

    @action
    def resume_download(self, url: Optional[str] = None, path: Optional[str] = None):
        """
        Resume a paused download.

        Either the URL or the path must be specified.

        :param url: URL of the download.
        :param path: Path of the download (default: any path associated with the URL).
        """
        for thread in self._get_downloads(url=url, path=path):
            thread.resume()

    @action
    def cancel_download(self, url: Optional[str] = None, path: Optional[str] = None):
        """
        Cancel a download in progress.

        Either the URL or the path must be specified.

        :param url: URL of the download.
        :param path: Path of the download (default: any path associated with the URL).
        """
        for thread in self._get_downloads(url=url, path=path):
            thread.stop()

    @action
    def clear_downloads(self, url: Optional[str] = None, path: Optional[str] = None):
        """
        Clear completed/cancelled downloads from the queue.

        :param url: URL of the download (default: all downloads).
        :param path: Path of the download (default: any path associated with the URL).
        """
        threads = (
            self._get_downloads(url=url, path=path)
            if url
            else list(self._download_threads.values())
        )

        for thread in threads:
            if thread.state not in (DownloadState.COMPLETED, DownloadState.CANCELLED):
                continue

            dl = self._download_threads.pop((thread.url, thread.path), None)
            if dl:
                dl.clear()

    @action
    def get_downloads(self, url: Optional[str] = None, path: Optional[str] = None):
        """
        Get the download threads.

        :param url: URL of the download (default: all downloads).
        :param path: Path of the download (default: any path associated with the URL).
        :return: .. schema:: media.download.MediaDownloadSchema(many=True)
        """
        from platypush.schemas.media.download import MediaDownloadSchema

        return MediaDownloadSchema().dump(
            (
                self._get_downloads(url=url, path=path)
                if url
                else list(self._download_threads.values())
            ),
            many=True,
        )

    def _get_downloads(self, url: Optional[str] = None, path: Optional[str] = None):
        assert url or path, 'URL or path must be specified'
        threads = []

        if url and path:
            path = os.path.expanduser(path)
            thread = self._download_threads.get((url, path))
            if thread:
                threads = [thread]
        elif url:
            threads = [
                thread
                for (url_, _), thread in self._download_threads.items()
                if url_ == url
            ]
        elif path:
            path = os.path.expanduser(path)
            threads = [
                thread
                for (_, path_), thread in self._download_threads.items()
                if path_ == path
            ]

        assert threads, f'No matching downloads found for [url={url}, path={path}]'
        return threads

    def _get_download_path(
        self,
        url: str,
        directory: Optional[str] = None,
        filename: Optional[str] = None,
        youtube_format: Optional[str] = None,
    ) -> str:
        if not directory:
            directory = self.download_dir

        directory = os.path.expanduser(directory)
        youtube_format = youtube_format or self.youtube_format

        if self._is_youtube_resource(url):
            with subprocess.Popen(
                [
                    self._ytdl,
                    *(
                        [
                            '-f',
                            youtube_format,
                        ]
                        if youtube_format
                        else []
                    ),
                    '-O',
                    '%(title)s.%(ext)s',
                    url,
                ],
                stdout=subprocess.PIPE,
            ) as proc:
                assert proc.stdout, 'yt-dlp stdout is None'
                filename = proc.stdout.read().decode()[:-1]

        if not filename:
            filename = url.split('/')[-1]

        return os.path.join(directory, filename)

    def _download_url(self, url: str, path: str, timeout: int) -> FileDownloadThread:
        download_thread = FileDownloadThread(
            url=url,
            path=path,
            timeout=timeout,
            on_start=self._on_download_start,
            post_event=self._post_event,
            stop_event=self._should_stop,
        )

        self._start_download(download_thread)
        return download_thread

    def _download_youtube_url(
        self,
        url: str,
        path: str,
        youtube_format: Optional[str] = None,
        only_audio: bool = False,
    ) -> YouTubeDownloadThread:
        download_thread = YouTubeDownloadThread(
            url=url,
            path=path,
            ytdl=self._ytdl,
            only_audio=only_audio,
            youtube_format=youtube_format or self.youtube_format,
            on_start=self._on_download_start,
            post_event=self._post_event,
            stop_event=self._should_stop,
        )

        self._start_download(download_thread)
        return download_thread

    def _on_download_start(self, thread: DownloadThread):
        self._download_threads[thread.url, thread.path] = thread

    def _start_download(self, thread: DownloadThread):
        if (thread.url, thread.path) in self._download_threads:
            self.logger.warning(
                'A download of %s to %s is already in progress', thread.url, thread.path
            )
            return

        thread.start()

    def _post_event(self, event_type: Type[MediaEvent], **kwargs):
        evt = event_type(
            player=get_plugin_name_by_class(self.__class__), plugin=self, **kwargs
        )
        self._bus.post(evt)

    def is_local(self):
        return self._is_local

    @staticmethod
    def get_subtitles_file(subtitles: Optional[str] = None):
        if not subtitles:
            return None

        if subtitles.startswith('file://'):
            subtitles = subtitles[len('file://') :]
        if os.path.isfile(subtitles):
            return os.path.abspath(subtitles)

        content = requests.get(subtitles, timeout=20).content
        f = tempfile.NamedTemporaryFile(
            prefix='media_subs_', suffix='.srt', delete=False
        )

        with f:
            f.write(content)
        return f.name

    def main(self):
        self.wait_stop()


__all__ = [
    'DownloadState',
    'MediaPlugin',
    'PlayerState',
]


# vim:sw=4:ts=4:et:
