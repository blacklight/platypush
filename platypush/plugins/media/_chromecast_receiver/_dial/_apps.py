import abc
import enum
import logging
import re
import threading
import time
import urllib.parse
import uuid
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class DialAppState(enum.Enum):
    STOPPED = 'stopped'
    RUNNING = 'running'


@dataclass
class DialApp(abc.ABC):
    name: str
    state: DialAppState = DialAppState.STOPPED
    run_id: Optional[str] = None

    @abc.abstractmethod
    def parse_payload(self, raw_payload: str) -> dict:
        """
        Parse URL-encoded DIAL launch payload.
        Raises ValueError on malformed or disallowed input.
        """

    @abc.abstractmethod
    def build_launch_kwargs(self, parsed: dict) -> dict:
        """
        Convert parsed payload into **kwargs for MediaPlugin.play().
        """

    def start(self) -> str:
        """Mark running; return opaque run ID."""
        self.run_id = uuid.uuid4().hex
        self.state = DialAppState.RUNNING
        return self.run_id

    def stop(self):
        self.state = DialAppState.STOPPED
        self.run_id = None


@dataclass
class MediaApp(DialApp):
    """
    Platypush-specific DIAL app for direct URL playback.

    POST payload (URL-encoded):
        url=<percent-encoded playback URL>   (required)
        type=<MIME type>                     (optional)

    Allowed URL schemes: http, https, rtsp, rtmp, hls.
    """

    name: str = 'Media'
    _ALLOWED_SCHEMES: ClassVar[frozenset] = frozenset(
        {'http', 'https', 'rtsp', 'rtmp', 'hls'}
    )

    def parse_payload(self, raw_payload: str) -> dict:
        params = urllib.parse.parse_qs(raw_payload, keep_blank_values=False)
        urls = params.get('url', [])
        if not urls:
            raise ValueError('Missing required "url" parameter')
        url = urls[0]
        scheme = urllib.parse.urlparse(url).scheme
        if scheme not in self._ALLOWED_SCHEMES:
            raise ValueError(
                f'URL scheme "{scheme}" not allowed; '
                f'allowed: {sorted(self._ALLOWED_SCHEMES)}'
            )
        result: dict = {'url': url}
        types = params.get('type', [])
        if types:
            result['content_type'] = types[0]
        return result

    def build_launch_kwargs(self, parsed: dict) -> dict:
        kwargs = {'resource': parsed['url']}
        if 'content_type' in parsed:
            kwargs['metadata'] = {'content_type': parsed['content_type']}
        return kwargs


@dataclass
class YouTubeApp(DialApp):
    """
    **Experimental** DIAL app for YouTube launch via yt-dlp resolution.

    This app has not been validated against a real YouTube DIAL sender.
    It may not handle all sender payload variants (queueing, pairing,
    playback synchronization).  Enable only for testing.

    POST payload (URL-encoded, standard YouTube DIAL grammar):
        v=<VIDEO_ID>        (required)
        t=<start_seconds>   (optional)
        list=<PLAYLIST_ID>  (optional, ignored in first implementation)

    Requires yt-dlp to be installed; resolution is delegated to
    MediaPlugin which uses yt-dlp internally.

    Note on start time: the ``t`` parameter is translated to an mpv
    ``start`` option. Backends that do not accept mpv-style options
    will not honour the start time.
    """

    name: str = 'YouTube'

    def parse_payload(self, raw_payload: str) -> dict:
        params = urllib.parse.parse_qs(raw_payload)
        videos = params.get('v', [])
        if not videos:
            raise ValueError('Missing required "v" (video ID) in YouTube payload')
        video_id = videos[0]
        if not re.fullmatch(r'[A-Za-z0-9_-]{5,20}', video_id):
            raise ValueError(f'Invalid YouTube video ID: {video_id}')
        result: dict = {'video_id': video_id}
        starts = params.get('t', [])
        if starts:
            try:
                result['start_time'] = float(starts[0])
            except ValueError:
                pass  # Ignore unparseable start time
        return result

    def build_launch_kwargs(self, parsed: dict) -> dict:
        url = f'https://www.youtube.com/watch?v={parsed["video_id"]}'
        kwargs: dict = {'resource': url}
        if 'start_time' in parsed:
            # mpv accepts the `start` option; other backends may ignore it.
            kwargs['start'] = parsed['start_time']
        return kwargs


class DialAppRegistry:
    """
    Thread-safe registry of installed DIAL apps. Owned by DialService (main process).
    """

    _APP_CLASSES: Dict[str, Type[DialApp]] = {
        'Media': MediaApp,
        'YouTube': YouTubeApp,
    }

    #: Grace period (seconds) after a DIAL launch during which idle polls
    #: will not clear the active app.  This allows the media backend time
    #: to transition from idle to playing without prematurely marking the
    #: app as stopped.
    LAUNCH_GRACE_SECS: float = 5.0

    def __init__(self, supported_apps: List[str]):
        self._lock = threading.RLock()
        self._launch_lock = threading.RLock()
        self._apps: Dict[str, DialApp] = {}
        self._active_app: Optional[str] = None
        self._launch_time: Optional[float] = None
        self._playback_observed: bool = False

        for name in supported_apps:
            cls = self._APP_CLASSES.get(name)
            if cls:
                self._apps[name] = cls(name)
                logger.debug('Registered DIAL app: %s', name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, app_id: str) -> Optional[DialApp]:
        with self._lock:
            return self._apps.get(app_id)

    def list_app_ids(self) -> List[str]:
        with self._lock:
            return list(self._apps.keys())

    def get_active_app(self) -> Optional[DialApp]:
        with self._lock:
            if not self._active_app:
                return None
            return self._apps.get(self._active_app)

    def launch(self, app_id: str, raw_payload: str, plugin) -> str:
        """
        Validate payload, stop any running app, call plugin.play(), return run_id.

        Raises
        ------
        KeyError     If app_id is not registered.
        ValueError   If the payload is malformed or contains disallowed input.
        RuntimeError If plugin.play() raises.
        """
        with self._launch_lock:
            with self._lock:
                app = self._apps.get(app_id)
                if app is None:
                    raise KeyError(f'Unknown DIAL app: {app_id}')

                # Validate payload before touching any live state.
                parsed = app.parse_payload(raw_payload)
                kwargs = app.build_launch_kwargs(parsed)

                if self._active_app and self._active_app != app_id:
                    self._stop_active_locked(plugin)

            try:
                plugin.play(**kwargs)
            except Exception as e:
                raise RuntimeError(f'plugin.play() failed: {e}') from e

            with self._lock:
                run_id = app.start()
                self._active_app = app_id
                self._launch_time = time.monotonic()
                self._playback_observed = False
                logger.info('DIAL app launched: %s run_id=%s', app_id, run_id)
                return run_id

    def stop(self, app_id: str, plugin) -> None:
        """
        Stop app_id and call plugin.stop().

        Raises
        ------
        KeyError   If app_id is not registered.
        ValueError If the app is not currently running.
        """
        with self._lock:
            app = self._apps.get(app_id)
            if app is None:
                raise KeyError(f'Unknown DIAL app: {app_id}')
            if app.state != DialAppState.RUNNING:
                raise ValueError(f'App {app_id} is not running')
            self._stop_active_locked(plugin)

    def notify_playback_active(self):
        """
        Called when the status loop observes non-idle playback.
        Marks that playback was observed so the launch grace period is no longer
        needed for future idle transitions.
        """
        with self._lock:
            if self._active_app:
                self._playback_observed = True

    def within_launch_grace(self) -> bool:
        """
        Return ``True`` if a DIAL app was recently launched and the media
        backend has not yet been observed playing.  During this window idle
        polls should not clear the active app.
        """
        with self._lock:
            if not self._active_app or not self._launch_time:
                return False
            if self._playback_observed:
                return False
            return (time.monotonic() - self._launch_time) < self.LAUNCH_GRACE_SECS

    def notify_playback_stopped(self):
        """
        Called when the plugin transitions to idle.
        Clears active app without calling plugin.stop() (already stopped externally).
        """
        with self._lock:
            if not self._active_app:
                return
            app = self._apps.get(self._active_app)
            if app:
                app.stop()
                logger.debug('DIAL app %s cleared (external stop)', self._active_app)
            self._active_app = None
            self._launch_time = None
            self._playback_observed = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _stop_active_locked(self, plugin):
        """Must be called with self._lock held."""
        if not self._active_app:
            return
        app = self._apps.get(self._active_app)
        if app:
            try:
                plugin.stop()
            except Exception as e:
                logger.warning('plugin.stop() error during DIAL stop: %s', e)
            app.stop()
            logger.info('DIAL app stopped: %s', self._active_app)
        self._active_app = None
        self._launch_time = None
        self._playback_observed = False
