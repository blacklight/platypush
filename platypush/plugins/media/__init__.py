import os
import pathlib
import queue
import tempfile
import threading
from abc import ABC, abstractmethod
from typing import (
    Dict,
    Iterable,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from urllib.parse import urlparse

import requests

from platypush.config import Config
from platypush.context import get_plugin, get_backend
from platypush.message.event.media import MediaEvent
from platypush.plugins import RunnablePlugin, action
from platypush.utils import (
    get_default_downloads_dir,
    get_mime_type,
    get_plugin_name_by_class,
)

from ._constants import audio_extensions, video_extensions
from ._model import DownloadState, MediaDirectory, PlayerState
from ._resource import MediaResource
from ._resource.downloaders import DownloadThread, MediaResourceDownloader, downloaders
from ._resource.parsers import MediaResourceParser, parsers
from ._search import MediaSearcher, searchers

_MediaDirs = Union[str, Iterable[Union[str, dict]], Dict[str, Union[str, dict]]]


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

    audio_extensions = audio_extensions
    video_extensions = video_extensions
    supported_media_plugins = [
        'media.vlc',
        'media.mpv',
        'media.gstreamer',
        'media.mplayer',
        'media.chromecast',
        'media.kodi',
    ]

    _supported_media_types = ['file', 'jellyfin', 'plex', 'torrent', 'youtube']
    _default_search_timeout = 60  # 60 seconds

    def __init__(
        self,
        media_dirs: Optional[_MediaDirs] = None,
        download_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        volume: Optional[Union[float, int]] = None,
        torrent_plugin: str = 'torrent',
        youtube_format: Optional[str] = 'bv[height<=?1080]+ba/bv+ba',
        youtube_audio_format: Optional[str] = 'ba',
        youtube_dl: str = 'yt-dlp',
        merge_output_format: str = 'mp4',
        cache_dir: Optional[str] = None,
        cache_streams: bool = False,
        ytdl_args: Optional[Sequence[str]] = None,
        **kwargs,
    ):
        """
        :param media_dirs: Directories that will be scanned for media files when
            a search is performed (default: only ``download_dir``). You can
            specify it either:

                - As a list of strings:

                  .. code-block:: yaml

                    media_dirs:
                        - /mnt/hd/media/movies
                        - /mnt/hd/media/music
                        - /mnt/hd/media/series

                - As a dictionary where the key is the name of the media display
                  name and the value is the path:

                    .. code-block:: yaml

                      media_dirs:
                          Movies: /mnt/hd/media/movies
                          Music: /mnt/hd/media/music
                          Series: /mnt/hd/media/series

                - As a dictionary where the key is the name of the media display
                  name and the value is a dictionary with the path and additional
                  display information:

                      media_dirs:
                          Movies:
                              path: /mnt/hd/media/movies
                              icon:
                                  url: https://example.com/icon.png
                                  # FontAwesome icon classes are supported
                                  class: fa fa-film

                          Music:
                              path: /mnt/hd/media/music
                              icon:
                                  url: https://example.com/icon.png
                                  class: fa fa-music

                          Series:
                              path: /mnt/hd/media/series
                              icon:
                                  url: https://example.com/icon.png
                                  class: fa fa-tv

        :param download_dir: Directory where external resources/torrents will be
            downloaded (default: ~/Downloads)
        :param env: Environment variables key-values to pass to the
            player executable (e.g. DISPLAY, XDG_VTNR, PULSE_SINK etc.)
        :param volume: Default volume for the player (default: None, maximum volume).
        :param torrent_plugin: Optional plugin to be used for torrent download.
            Possible values:

                - ``torrent`` - native ``libtorrent``-based plugin (default,
                  recommended)
                - ``rtorrent`` - torrent support over rtorrent RPC/XML interface
                - ``webtorrent`` - torrent support over webtorrent (unstable)

        :param youtube_format: Select the preferred video/audio format for
            YouTube videos - and any media supported by youtube-dl or the
            selected fork. See the `youtube-dl documentation
            <https://github.com/ytdl-org/youtube-dl#format-selection>`_ for more
            info on supported formats. Example:
            ``bestvideo[height<=?1080][ext=mp4]+bestaudio`` - select the best
            mp4 video with a resolution <= 1080p, and the best audio format.
        :param youtube_audio_format: Select the preferred audio format for
            YouTube videos downloaded only for audio. Default: ``bestaudio``.
        :param youtube_dl: Path to the ``youtube-dl`` executable, used to
            extract information from YouTube videos and other media platforms.
            Default: ``yt-dlp``. The default has changed from ``youtube-dl`` to
            the ``yt-dlp`` fork because the former is badly maintained and its
            latest release was pushed in 2021.
        :param merge_output_format: If media download requires ``youtube_dl``,
            and the upstream media contains both audio and video to be merged,
            this can be used to specify the format of the output container -
            e.g. ``mp4``, ``mkv``, ``avi``, ``flv``. Default: ``mp4``.
        :param cache_dir: Directory where the media cache will be stored. If not
            specified, the cache will be stored in the default cache directory
            (usually ``~/.cache/platypush/media/<media_plugin>``).
        :param cache_streams: If set to True, streams transcoded via yt-dlp or
            ffmpeg will be cached in ``cache_dir`` directory. If not set
            (default), then streams will be played directly via memory pipe.
            You may want to set this to True if you have a slow network, or if
            you want to play media at high quality, even though the start time
            may be delayed. If set to False, the media will start playing as
            soon as the stream is ready, but the quality may be lower,
            especially at the beginning, and seeking may not be supported.
        :param ytdl_args: Additional arguments to pass to the youtube-dl
            executable. Default: None.
        """

        super().__init__(**kwargs)

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

        if self.__class__.__name__ == 'MediaPlugin':
            # Populate this plugin with the actions of the configured player
            for act in player.registered_actions:
                setattr(self, act, getattr(player, act))
                self.registered_actions.add(act)

        self._env = env or {}
        self.cache_streams = cache_streams
        self.download_dir = os.path.abspath(
            os.path.expanduser(
                download_dir
                or player_config.get('download_dir')
                or get_default_downloads_dir()
            )
        )

        self.cache_dir = os.path.abspath(
            os.path.expanduser(cache_dir)
            if cache_dir
            else os.path.join(
                Config.get_cachedir(),
                'media',
                get_plugin_name_by_class(self.__class__),
            )
        )

        pathlib.Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        self._ytdl = youtube_dl
        self.volume = volume
        self._videos_queue = []
        self._youtube_proc = None
        self.torrent_plugin = torrent_plugin
        self.youtube_format = youtube_format
        self.youtube_audio_format = youtube_audio_format
        self.merge_output_format = merge_output_format
        self.ytdl_args = ytdl_args or []
        self._latest_resource: Optional[MediaResource] = None

        self.media_dirs = self._parse_media_dirs(
            media_dirs or player_config.get('media_dirs', [])
        )

        self._parsers: Dict[Type[MediaResourceParser], MediaResourceParser] = {
            parser: parser(self) for parser in parsers
        }

        self._downloaders: Dict[
            Type[MediaResourceDownloader], MediaResourceDownloader
        ] = {downloader: downloader(self) for downloader in downloaders}

        self._searchers: Dict[Type[MediaSearcher], MediaSearcher] = {
            searcher: searcher(
                dirs=[d.path for d in self.media_dirs.values()], media_plugin=self
            )
            for searcher in searchers
        }

    @staticmethod
    def _parse_media_dirs(
        media_dirs: Optional[_MediaDirs],
    ) -> Dict[str, MediaDirectory]:
        dirs = {}

        if media_dirs:
            if isinstance(media_dirs, str):
                dirs = [media_dirs]
            if isinstance(media_dirs, (list, tuple, set)):
                dirs = {d: d for d in media_dirs}
            if isinstance(media_dirs, dict):
                dirs = media_dirs

        assert isinstance(dirs, dict), f'Invalid media_dirs format: {media_dirs}'

        ret = {}
        for k, v in dirs.items():
            assert isinstance(k, str), f'Invalid media_dirs key format: {k}'
            if isinstance(v, str):
                v = {'path': v}

            assert isinstance(v, dict), f'Invalid media_dirs format: {v}'
            path = v.get('path')
            assert path, f'Missing path in media_dirs entry {k}'
            path = os.path.abspath(os.path.expanduser(path))
            assert os.path.isdir(path), f'Invalid path in media_dirs entry {k}'

            icon = v.get('icon', {})
            if isinstance(icon, str):
                # Fill up the URL field if it's a URL, otherwise assume that
                # it's a FontAwesome icon class
                icon = {'url': icon} if urlparse(icon).scheme else {'class': icon}

            ret[k] = MediaDirectory.build(
                name=k,
                path=path,
                icon_class=icon.get('class'),
                icon_url=icon.get('url'),
            )

        # Add the downloads directory if it's missing
        if not any(d.path == get_default_downloads_dir() for d in ret.values()):
            ret['Downloads'] = MediaDirectory.build(
                name='Downloads',
                path=get_default_downloads_dir(),
                icon_class='fas fa-download',
            )

        return {k: ret[k] for k in sorted(ret.keys())}

    def _get_resource(
        self,
        resource: str,
        metadata: Optional[dict] = None,
        only_audio: bool = False,
        **_,
    ):
        """
        :param resource: Resource to play/parse. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)
            * Any URL that is supported by a yt_dlp extractor

        """

        for parser in self._parsers.values():
            media_resource = parser.parse(resource, only_audio=only_audio)
            if media_resource:
                for k, v in (metadata or {}).items():
                    setattr(media_resource, k, v)

                return media_resource

        raise AssertionError(f'Unknown media resource: {resource}')

    @action
    @abstractmethod
    def play(self, resource: str, **kwargs):
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
        searcher = next(
            iter(filter(lambda s: s.supports(search_type), self._searchers.values())),
            None,
        )

        if not searcher:
            self.logger.warning('Unsupported search type: %s', search_type)
            return None

        return searcher

    @classmethod
    def is_video_file(cls, filename: str):
        if filename.lower().split('.')[-1] in cls.video_extensions:
            return True

        mime_type = get_mime_type(filename)
        return bool(mime_type and mime_type.startswith('video/'))

    @classmethod
    def is_audio_file(cls, filename: str):
        if filename.lower().split('.')[-1] in cls.audio_extensions:
            return True

        mime_type = get_mime_type(filename)
        return bool(mime_type and mime_type.startswith('audio/'))

    @classmethod
    def is_media_file(cls, file: str) -> bool:
        if file.split('.')[-1].lower() in cls.video_extensions.union(
            cls.audio_extensions
        ):
            return True

        mime_type = get_mime_type(file)
        return bool(
            mime_type
            and (mime_type.startswith('video/') or mime_type.startswith('audio/'))
        )

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

    @action
    def get_info(self, resource: str):
        for parser in self._parsers.values():
            info = parser.parse(resource)
            if info:
                return info.to_dict()

        return {'url': resource}

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
        youtube_audio_format: Optional[str] = None,
        merge_output_format: Optional[str] = None,
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
        :param youtube_audio_format: Override the default ``youtube_audio_format``
        :param merge_output_format: Override the default
            ``merge_output_format`` setting.
        :return: The absolute path to the downloaded file.
        """
        dl_thread = None
        resource = self._get_resource(url, only_audio=only_audio)

        if filename:
            path = os.path.expanduser(filename)
        elif resource.filename:
            path = resource.filename
        else:
            path = os.path.basename(resource.url)

        if not os.path.isabs(path):
            directory = os.path.expanduser(directory or self.download_dir)
            path = os.path.join(directory, path)

        for downloader in self._downloaders.values():
            if downloader.supports(resource):
                if only_audio and not downloader.supports_only_audio():
                    self.logger.warning(
                        'Only audio download is not supported for this resource'
                    )

                dl_thread = downloader.download(
                    resource=resource,
                    path=path,
                    timeout=timeout,
                    only_audio=only_audio,
                    youtube_format=youtube_format or self.youtube_format,
                    youtube_audio_format=youtube_audio_format
                    or self.youtube_audio_format,
                    merge_output_format=merge_output_format,
                )

                break

        assert dl_thread, f'No downloader found for resource {url}'

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

    @action
    def get_media_dirs(self) -> Dict[str, dict]:
        """
        :return: List of configured media directories.
        """
        return {dir.name: dir.to_dict() for dir in self.media_dirs.values()}

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

    def on_download_start(self, thread: DownloadThread):
        self._download_threads[thread.url, thread.path] = thread

    def start_download(self, thread: DownloadThread):
        if (thread.url, thread.path) in self._download_threads:
            self.logger.warning(
                'A download of %s to %s is already in progress', thread.url, thread.path
            )
            return

        thread.start()

    def post_event(self, event_type: Type[MediaEvent], **kwargs):
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

    @property
    def supports_local_media(self) -> bool:
        return True

    @property
    def supports_local_pipe(self) -> bool:
        return True

    def main(self):
        self.wait_stop()


__all__ = [
    'DownloadState',
    'MediaPlugin',
    'MediaResource',
    'MediaSearcher',
    'PlayerState',
]


# vim:sw=4:ts=4:et:
