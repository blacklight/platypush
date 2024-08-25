import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Type

from platypush.message.event.media import (
    MediaDownloadCancelledEvent,
    MediaDownloadClearEvent,
    MediaDownloadCompletedEvent,
    MediaDownloadErrorEvent,
    MediaDownloadEvent,
    MediaDownloadPausedEvent,
    MediaDownloadProgressEvent,
    MediaDownloadResumedEvent,
    MediaDownloadStartedEvent,
)
from platypush.plugins.media._model import DownloadState
from platypush.plugins.media._resource import MediaResource


class MediaResourceDownloader(ABC):
    """
    Base media resource downloader class.
    """

    def __init__(self, media_plugin, *_, **__):
        from platypush.plugins.media import MediaPlugin

        self._media: MediaPlugin = media_plugin

    @abstractmethod
    def download(
        self, resource: MediaResource, path: Optional[str] = None, **_
    ) -> 'DownloadThread':
        pass

    def get_download_path(
        self,
        resource: MediaResource,
        *_,
        directory: Optional[str] = None,
        filename: Optional[str] = None,
        **__,
    ) -> str:
        directory = (
            os.path.expanduser(directory) if directory else self._media.download_dir
        )

        if not filename:
            filename = resource.filename or resource.url.split('/')[-1]

        return os.path.join(directory, filename)

    @abstractmethod
    def supports(self, resource_type: MediaResource) -> bool:
        return False

    def supports_only_audio(self) -> bool:
        return False


class DownloadThread(threading.Thread, ABC):
    """
    Thread that downloads a URL to a file.
    """

    _progress_update_interval = 1
    """ Throttle the progress updates to this interval, in seconds. """

    def __init__(
        self,
        path: str,
        url: str,
        post_event: Callable,
        size: Optional[int] = None,
        timeout: Optional[int] = 10,
        on_start: Callable[['DownloadThread'], None] = lambda _: None,
        on_close: Callable[['DownloadThread'], None] = lambda _: None,
        stop_event: Optional[threading.Event] = None,
    ):
        super().__init__(name=f'DownloadThread-{path}')
        self.path = path
        self.url = url
        self.size = size
        self.timeout = timeout
        self.state = DownloadState.IDLE
        self.progress = None
        self.started_at = None
        self.ended_at = None
        self._upstream_stop_event = stop_event or threading.Event()
        self._stop_event = threading.Event()
        self._post_event = post_event
        self._on_start = on_start
        self._on_close = on_close
        self._paused = threading.Event()
        self._downloading = threading.Event()
        self._last_progress_update_time = 0
        self.logger = logging.getLogger(__name__)

    def should_stop(self) -> bool:
        return self._stop_event.is_set() or self._upstream_stop_event.is_set()

    @abstractmethod
    def _run(self) -> bool:
        pass

    def pause(self):
        self.state = DownloadState.PAUSED
        self._paused.set()
        self._downloading.clear()
        self.post_event(MediaDownloadPausedEvent)

    def resume(self):
        self.state = DownloadState.DOWNLOADING
        self._paused.clear()
        self._downloading.set()
        self.post_event(MediaDownloadResumedEvent)

    def run(self):
        super().run()
        interrupted = False

        try:
            self.on_start()
            interrupted = not self._run()

            if interrupted:
                self.state = DownloadState.CANCELLED
            else:
                self.state = DownloadState.COMPLETED
        except Exception as e:
            self.state = DownloadState.ERROR
            self.post_event(MediaDownloadErrorEvent, error=str(e))
            self.logger.warning('Error while downloading URL: %s', e)
        finally:
            self.on_close()

    def stop(self):
        self.state = DownloadState.CANCELLED
        self._stop_event.set()
        self._downloading.clear()

    def on_start(self):
        self.state = DownloadState.STARTED
        self.started_at = time.time()
        self.post_event(MediaDownloadStartedEvent)
        self._on_start(self)

    def on_close(self):
        self.ended_at = time.time()
        if self.state == DownloadState.CANCELLED:
            self.post_event(MediaDownloadCancelledEvent)
        elif self.state == DownloadState.COMPLETED:
            self.post_event(MediaDownloadCompletedEvent)

        self._on_close(self)

    def clear(self):
        if self.state not in (DownloadState.COMPLETED, DownloadState.CANCELLED):
            self.logger.info(
                'Download thread for %s is still active, stopping', self.url
            )

            self.stop()
            self.join(timeout=10)

        self.post_event(MediaDownloadClearEvent)

    def post_event(self, event_type: Type[MediaDownloadEvent], **kwargs):
        kwargs = {
            'resource': self.url,
            'path': self.path,
            'state': self.state.value,
            'size': self.size,
            'timeout': self.timeout,
            'progress': self.progress,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            **kwargs,
        }

        self._post_event(event_type, **kwargs)

    def __setattr__(self, name: str, value: Optional[Any], /) -> None:
        if name == 'progress' and value is not None:
            if value < 0 or value > 100:
                self.logger.debug('Invalid progress value:%s', value)
                return

            prev_progress = getattr(self, 'progress', None)

            if prev_progress is None or (
                int(prev_progress) != int(value)
                and (
                    time.time() - self._last_progress_update_time
                    >= self._progress_update_interval
                )
            ):
                value = round(value, 2)
                self._last_progress_update_time = time.time()
                self.post_event(MediaDownloadProgressEvent, progress=value)

        super().__setattr__(name, value)


# vim:sw=4:ts=4:et:
