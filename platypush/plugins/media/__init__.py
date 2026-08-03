import base64
import json
import os
import pathlib
import queue
import tempfile
import threading
from abc import ABC, abstractmethod
from typing import (
    Any,
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
from platypush.message.event.media import (
    MediaEndEvent,
    MediaEvent,
    MediaQueueAddedEvent,
    MediaQueueClearedEvent,
    MediaQueueMovedEvent,
    MediaQueueRemovedEvent,
    MediaStopEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.utils import (
    get_default_downloads_dir,
    get_mime_type,
    get_plugin_name_by_class,
)

from ... import Response
from ._constants import audio_extensions, video_extensions
from ._model import DownloadState, MediaDirectory, PlayerState
from ._resource import MediaResource
from ._resource.downloaders import DownloadThread, MediaResourceDownloader, downloaders
from ._resource.parsers import MediaResourceParser, YoutubeResourceParser, parsers
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
    _videos_queue_lock = threading.RLock()

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
        chromecast_receiver: Optional[Dict[str, Any]] = None,
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
        :param chromecast_receiver: Optional configuration to expose this
            media plugin as a Chromecast receiver on the LAN. The HTTP backend
            must be configured, and the ``chromecast-receiver`` extra must be
            installed:

          .. code-block:: bash

            pip install platypush[chromecast-receiver]

          Example configuration:

          .. code-block:: yaml

            media.mpv:
                chromecast_receiver:
                    enabled: true
                    device_name: Living Room Platypush
                    host: 192.168.1.50
                    port: 8009
                    model_name: Platypush
                    manufacturer: Platypush
                    allowed_networks:
                        - 192.168.0.0/16
                        - 10.0.0.0/8
                    status_interval: 1.0
                    dial:
                        # To enable the DIAL protocol
                        enabled: true

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
        self._ytdl = os.path.expanduser(youtube_dl)
        self.volume = volume
        self._videos_queue = []
        self.register_handler(MediaEndEvent, self._on_media_end)
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

        if chromecast_receiver and chromecast_receiver.get('enabled'):
            from ._chromecast_receiver import ChromecastReceiverService

            self._chromecast_receiver_service = ChromecastReceiverService(
                self, chromecast_receiver
            )
        else:
            self._chromecast_receiver_service = None

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

        if not (isinstance(dirs, dict)):
            raise AssertionError(f'Invalid media_dirs format: {media_dirs}')

        ret = {}
        for k, v in dirs.items():
            if not (isinstance(k, str)):
                raise AssertionError(f'Invalid media_dirs key format: {k}')
            if isinstance(v, str):
                v = {'path': v}

            if not (isinstance(v, dict)):
                raise AssertionError(f'Invalid media_dirs format: {v}')
            path = v.get('path')
            if not path:
                raise AssertionError(f'Missing path in media_dirs entry {k}')
            path = os.path.abspath(os.path.expanduser(path))
            if not (os.path.isdir(path)):
                raise AssertionError(f'Invalid path in media_dirs entry {k}')

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

        ytid = YoutubeResourceParser.extract_youtube_id(resource)
        if ytid:
            resource = f'https://www.youtube.com/watch?v={ytid}'
            if metadata:
                metadata['url'] = resource

        for parser in self._parsers.values():
            media_resource = parser.parse(resource, only_audio=only_audio)
            if media_resource:
                for k, v in (metadata or {}).items():
                    setattr(media_resource, k, v)

                return media_resource

        raise AssertionError(f'Unknown media resource: {resource}')

    @action
    @abstractmethod
    def play(self, resource: Optional[str] = None, **kwargs):
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

    @staticmethod
    def _get_queue_item_url(item):
        """
        Extract the playable URL from a queue item. Queue items can be either
        plain URL strings or dictionaries containing a ``url`` key.
        """
        if isinstance(item, dict):
            return item.get('url')
        return item

    @staticmethod
    def _normalize_queue_item(item):
        """
        Normalize an item added to the queue into a dictionary with at least
        a ``url`` key, preserving any extra metadata passed by the caller.
        """
        if isinstance(item, dict):
            return item

        if isinstance(item, MediaResource):
            return item.to_dict()

        return {'url': item}

    def _resume_from_queue(self, resource: Optional[str]):
        """
        If no resource is given and the player is stopped with queued items,
        pop and play the next queued item. Returns the play() result or None.
        """
        if resource:
            return None

        if not self._videos_queue:
            return None

        state = getattr(self, '_state', None)
        if state is None:
            # noinspection PyBroadException
            try:
                status = self.status()
                if isinstance(status, Response):
                    status = status.output
                state = PlayerState((status or {}).get('state', PlayerState.STOP.value))
            except Exception:
                state = PlayerState.STOP

        if state != PlayerState.STOP:
            return None

        with self._videos_queue_lock:
            item = self._videos_queue.pop(0)

        self.post_event(MediaQueueRemovedEvent, item=item, index=0)

        url = self._get_queue_item_url(item)
        if not url:
            return None

        return self.play(url)

    @action
    def next(self, *args, **kwargs):
        """Play the next item in the queue or the player-specific playlist."""
        with self._videos_queue_lock:
            video = self._videos_queue.pop(0) if self._videos_queue else None

        if video:
            self.post_event(MediaQueueRemovedEvent, item=video, index=0)
            return self._play_queue_next(video)

        return self._next(*args, **kwargs)

    def _play_queue_next(self, item):
        """Stop playback and play the next queued item."""
        self.stop()
        return self.play(self._get_queue_item_url(item))

    def _next(self, *_, **__):
        """Player-specific next action when the queue is empty."""
        return None

    @action
    def add_to_queue(self, resource: Union[str, dict], index: Optional[int] = None):
        """
        Add a media item to the playback queue.

        :param resource: Media URL or media item dictionary to queue.
        :param index: Optional zero-based position where the item should be
            inserted. If not specified, the item is appended to the end of the
            queue.
        :return: The item that was added to the queue.
        """
        item = self._normalize_queue_item(resource)
        with self._videos_queue_lock:
            if index is None:
                self._videos_queue.append(item)
                index = len(self._videos_queue) - 1
            else:
                self._videos_queue.insert(index, item)

        self.post_event(MediaQueueAddedEvent, item=item, index=index)
        return item

    @action
    def pop_queue(self):
        """
        Remove and return the next item from the front of the playback queue.

        :return: The removed queue item, or ``None`` if the queue is empty.
        """
        with self._videos_queue_lock:
            if not self._videos_queue:
                return None

            item = self._videos_queue.pop(0)

        self.post_event(MediaQueueRemovedEvent, item=item, index=0)
        return item

    @action
    def remove_queue_item(self, index: int):
        """
        Remove an item from the playback queue by its index.

        :param index: Zero-based index of the item to remove.
        :return: The removed queue item.
        """
        with self._videos_queue_lock:
            if index < 0 or index >= len(self._videos_queue):
                raise IndexError(f'Queue index {index} out of range')

            item = self._videos_queue.pop(index)

        self.post_event(MediaQueueRemovedEvent, item=item, index=index)
        return item

    @action
    def move_queue_item(self, from_index: int, to_index: int):
        """
        Change the position of an item in the playback queue.

        :param from_index: Current zero-based index of the item.
        :param to_index: New zero-based index for the item.
        :return: The updated queue.
        """
        with self._videos_queue_lock:
            if from_index < 0 or from_index >= len(self._videos_queue):
                raise IndexError(f'Queue from_index {from_index} out of range')

            item = self._videos_queue.pop(from_index)
            self._videos_queue.insert(to_index, item)

        self.post_event(
            MediaQueueMovedEvent, item=item, from_index=from_index, to_index=to_index
        )
        return self._videos_queue

    @action
    def get_queue(self):
        """
        Get the items currently in the playback queue.

        :return: List of queued media items.
        """
        return self._videos_queue

    @action
    def clear_queue(self):
        """
        Clear the playback queue.

        :return: The number of items that were removed.
        """
        with self._videos_queue_lock:
            count = len(self._videos_queue)
            self._videos_queue = []

        self.post_event(MediaQueueClearedEvent, count=count)
        return count

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
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform a video search.

        :param query: Query string, video name or partial name
        :param types: Video types to search (default: ``["youtube", "file", "torrent"]``)
        :param queue_results: Append the results to the current playing queue (default: False)
        :param autoplay: Play the first result of the search (default: False)
        :param timeout: Search timeout (default: 60 seconds)
        :param limit: Maximum number of results per source per page
            (default: 25).
        :param page_token: Opaque pagination token returned by a previous
            search call as ``next_page_token``.  Pass it to retrieve the
            next page of results.
        :return: A dictionary with ``results`` (list of media items) and
            ``next_page_token`` (string or ``null`` when there are no more
            pages).
        """

        page_states = {}
        if page_token:
            try:
                page_states = json.loads(base64.b64decode(page_token).decode())
            except Exception:
                self.logger.warning('Invalid page token: %s', page_token)

        results = {}
        results_queues = {}
        worker_threads = {}

        if types is None:
            types = self._supported_media_types

        active_types = [t for t in types if not page_token or t in page_states]

        for media_type in active_types:
            results[media_type] = []
            results_queues[media_type] = queue.Queue()
            search_hndl = self._get_search_handler_by_type(media_type)
            if not search_hndl:
                continue

            worker_threads[media_type] = threading.Thread(
                target=self._search_worker(
                    query=query,
                    search_hndl=search_hndl,
                    results_queue=results_queues[media_type],
                    limit=limit,
                    page_state=page_states.get(media_type),
                )
            )
            worker_threads[media_type].start()

        next_page_states: Dict[str, dict] = {}
        for media_type in active_types:
            if media_type not in results_queues:
                continue

            try:
                result = results_queues[media_type].get(timeout=timeout)
                if isinstance(result, Exception):
                    raise result

                if isinstance(result, tuple):
                    items, next_state = result
                else:
                    items, next_state = result, None

                results[media_type].extend(items or [])
                if next_state:
                    next_page_states[media_type] = next_state
            except queue.Empty:
                self.logger.warning(
                    'Search for "%s" media type %s timed out', query, media_type
                )
            except Exception as e:
                self.logger.warning(
                    'Error while searching for "%s", media type %s', query, media_type
                )
                self.logger.exception(e)

        flat_results = [
            {**result, 'type': media_type}
            for media_type in self._supported_media_types
            for result in results.get(media_type, [])
            if media_type in results
        ]

        if flat_results:
            if queue_results:
                self._videos_queue = flat_results
                if autoplay:
                    self.play(self._videos_queue.pop(0).get('url'))
            elif autoplay:
                self.play(flat_results[0]['url'])

        next_token = (
            base64.b64encode(json.dumps(next_page_states).encode()).decode()
            if next_page_states
            else None
        )

        return {
            'results': flat_results,
            'next_page_token': next_token,
        }

    @staticmethod
    def _search_worker(query, search_hndl, results_queue, limit=None, page_state=None):
        def thread():
            try:
                results_queue.put(
                    search_hndl.search(query, limit=limit, page_state=page_state)
                )
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
        if not http:
            raise AssertionError(
                f'Unable to stream {media}: HTTP backend not configured'
            )

        self.logger.info('Starting streaming %s', media)
        response = requests.put(
            f'{http.local_base_url}/media' + ('?download' if download else ''),
            json={'source': media, 'subtitles': subtitles},
            timeout=300,
        )

        if not response.ok:
            raise AssertionError(response.text or response.reason)
        return response.json()

    @action
    def stop_streaming(self, media_id: str):
        http = get_backend('http')
        if not http:
            raise AssertionError(
                f'Unable to stop streaming {media_id}: HTTP backend not configured'
            )

        response = requests.delete(
            f'{http.local_base_url}/media/{media_id}', timeout=30
        )

        if not response.ok:
            raise AssertionError(response.text or response.reason)
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

        if not dl_thread:
            raise AssertionError(f'No downloader found for resource {url}')

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
        return {dir_.name: dir_.to_dict() for dir_ in self.media_dirs.values()}

    def _get_downloads(self, url: Optional[str] = None, path: Optional[str] = None):
        if not (url or path):
            raise AssertionError('URL or path must be specified')
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

        if not threads:
            raise AssertionError(
                f'No matching downloads found for [url={url}, path={path}]'
            )
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
        plugin_name = get_plugin_name_by_class(self.__class__)
        evt = event_type(player=plugin_name, plugin=plugin_name, **kwargs)
        self.fire_event(evt)

    def _on_media_end(self, event: MediaEndEvent):
        """Autoplay the next item in the queue when a media item naturally ends."""
        if isinstance(event, MediaStopEvent):
            self.logger.debug(
                'Ignoring MediaStopEvent in _on_media_end: not a natural end'
            )
            return

        if getattr(self, '_user_stopped', False):
            self.logger.debug(
                'Ignoring MediaEndEvent: the player was explicitly stopped'
            )
            return

        self._play_next_queue()

    def _play_next_queue(self):
        """Pop the next item from the queue and play it."""
        with self._videos_queue_lock:
            if not self._videos_queue:
                # The queue has ended, emit a MediaStopEvent
                self.post_event(MediaStopEvent)
                return

            item = self._videos_queue.pop(0)

        self.post_event(MediaQueueRemovedEvent, item=item, index=0)
        try:
            self.play(self._get_queue_item_url(item))
        except Exception as e:
            self.logger.exception(e)

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
        if self._chromecast_receiver_service:
            try:
                self._chromecast_receiver_service.start()
            except Exception as e:
                self.logger.warning(
                    'Could not start Chromecast receiver service: %s', e
                )

        try:
            self.wait_stop()
        finally:
            if self._chromecast_receiver_service:
                self._chromecast_receiver_service.stop()


__all__ = [
    'DownloadState',
    'MediaPlugin',
    'MediaResource',
    'MediaSearcher',
    'PlayerState',
]


# vim:sw=4:ts=4:et:
