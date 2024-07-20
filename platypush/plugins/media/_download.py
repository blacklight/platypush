from abc import ABC, abstractmethod
from contextlib import suppress
from enum import Enum
import json
import logging
import signal
import subprocess
import threading
import time
from typing import Any, Callable, Optional, Type

import requests

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

from platypush.utils import wait_for_either


class DownloadState(Enum):
    """
    Enum that represents the status of a download.
    """

    IDLE = 'idle'
    STARTED = 'started'
    DOWNLOADING = 'downloading'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ERROR = 'error'


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


class FileDownloadThread(DownloadThread):
    """
    Thread that downloads a generic URL to a file.
    """

    def _run(self):
        interrupted = False

        with requests.get(self.url, timeout=self.timeout, stream=True) as response:
            response.raise_for_status()
            self.size = int(response.headers.get('Content-Length', 0)) or None

            with open(self.path, 'wb') as f:
                self.on_start()

                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk or self.should_stop():
                        interrupted = self.should_stop()
                        if interrupted:
                            self.stop()

                        break

                    self.state = DownloadState.DOWNLOADING
                    f.write(chunk)
                    percent = f.tell() / self.size * 100 if self.size else 0
                    self.progress = percent

                    if self._paused.is_set():
                        wait_for_either(self._downloading, self._stop_event)

        return not interrupted


class YouTubeDownloadThread(DownloadThread):
    """
    Thread that downloads a YouTube URL to a file.
    """

    def __init__(
        self,
        *args,
        ytdl: str,
        youtube_format: Optional[str] = None,
        only_audio: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._ytdl = ytdl
        self._youtube_format = youtube_format
        self._only_audio = only_audio
        self._proc = None
        self._proc_lock = threading.Lock()

    def _parse_progress(self, line: str):
        try:
            progress = json.loads(line)
        except json.JSONDecodeError:
            return

        status = progress.get('status')
        if not status:
            return

        if status == 'finished':
            self.progress = 100
            return

        if status == 'paused':
            self.state = DownloadState.PAUSED
        elif status == 'downloading':
            self.state = DownloadState.DOWNLOADING

        self.size = int(progress.get('total_bytes_estimate', 0)) or self.size
        if self.size:
            downloaded = int(progress.get('downloaded_bytes', 0))
            self.progress = (downloaded / self.size) * 100

    def _run(self):
        ytdl_cmd = [
            self._ytdl,
            '--newline',
            '--progress',
            '--progress-delta',
            str(self._progress_update_interval),
            '--progress-template',
            '%(progress)j',
            *(['-x'] if self._only_audio else []),
            *(['-f', self._youtube_format] if self._youtube_format else []),
            self.url,
            '-o',
            self.path,
        ]

        self.logger.info('Executing command %r', ytdl_cmd)
        err = None

        with subprocess.Popen(ytdl_cmd, stdout=subprocess.PIPE) as self._proc:
            if self._proc.stdout:
                for line in self._proc.stdout:
                    self.logger.debug(
                        '%s output: %s', self._ytdl, line.decode().strip()
                    )

                    self._parse_progress(line.decode())

                    if self.should_stop():
                        self.stop()
                        return self._proc.returncode == 0

                    if self._paused.is_set():
                        wait_for_either(self._downloading, self._stop_event)

        if self._proc.returncode != 0:
            err = self._proc.stderr.read().decode() if self._proc.stderr else None
            raise RuntimeError(
                f'{self._ytdl} failed with return code {self._proc.returncode}: {err}'
            )

        return True

    def pause(self):
        with self._proc_lock:
            if self._proc:
                self._proc.send_signal(signal.SIGSTOP)

        super().pause()

    def resume(self):
        with self._proc_lock:
            if self._proc:
                self._proc.send_signal(signal.SIGCONT)

        super().resume()

    def stop(self):
        state = None

        with suppress(IOError, OSError), self._proc_lock:
            if self._proc:
                if self._proc.poll() is None:
                    self._proc.terminate()
                    self._proc.wait(timeout=3)
                    if self._proc.returncode is None:
                        self._proc.kill()

                    state = DownloadState.CANCELLED
                elif self._proc.returncode != 0:
                    state = DownloadState.ERROR
                else:
                    state = DownloadState.COMPLETED

                self._proc = None

        super().stop()

        if state:
            self.state = state

    def on_close(self):
        self.stop()
        super().on_close()
